import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from .auth import validate_api_key
from .codeberg import parse_codeberg_rss
from .config import settings
from .db import SessionLocal, engine
from .models import Base, Event
from .queue import enqueue
from .reliability import verify_signature
from .schemas import EventRequest, EventResponse
from .websocket import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as c:
        await c.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title='HAMYLION Core', version='3.1.0', lifespan=lifespan)


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': 'hamylion-core', 'version': '3.1.0'}


@app.get('/ready')
async def ready():
    try:
        async with SessionLocal() as s:
            await s.execute(select(Event.id).limit(1))
        return {'ready': True}
    except Exception:
        return {'ready': False}


@app.post('/v1/events', response_model=EventResponse)
async def create_event(req: EventRequest, project_id: str = Depends(validate_api_key)):
    async with SessionLocal() as s:
        existing = (await s.execute(select(Event).where(
            Event.project_id == project_id,
            Event.idempotency_key == req.idempotency_key,
        ))).scalar_one_or_none()
        if existing:
            return EventResponse(event_id=existing.id, status=existing.status, replayed=True)

        eid = 'evt_' + uuid.uuid4().hex
        event = Event(
            id=eid,
            project_id=project_id,
            event_type=req.type,
            idempotency_key=req.idempotency_key,
            payload=req.payload,
        )
        s.add(event)
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()
            existing = (await s.execute(select(Event).where(
                Event.project_id == project_id,
                Event.idempotency_key == req.idempotency_key,
            ))).scalar_one()
            return EventResponse(event_id=existing.id, status=existing.status, replayed=True)

    try:
        await enqueue({'id': eid, 'project_id': project_id, 'type': req.type, 'payload': req.payload, 'attempt': 1})
        async with SessionLocal() as s:
            await s.execute(update(Event).where(Event.id == eid).values(published_at=datetime.utcnow()))
            await s.commit()
    except Exception:
        pass

    return EventResponse(event_id=eid, status='queued')


@app.post('/v1/github/webhook')
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    if not settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail='GITHUB_WEBHOOK_SECRET is not configured')

    body = await request.body()
    if not verify_signature(settings.GITHUB_WEBHOOK_SECRET, body, x_hub_signature_256 or ''):
        raise HTTPException(status_code=401, detail='invalid GitHub webhook signature')
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail='missing X-GitHub-Delivery')

    payload = json.loads(body.decode('utf-8'))
    event_type = 'github.' + (x_github_event or 'unknown')
    project_id = str(payload.get('repository', {}).get('full_name') or 'github')
    eid = 'evt_' + uuid.uuid4().hex

    async with SessionLocal() as s:
        existing = (await s.execute(select(Event).where(
            Event.project_id == project_id,
            Event.idempotency_key == x_github_delivery,
        ))).scalar_one_or_none()
        if existing:
            return {'event_id': existing.id, 'status': existing.status, 'replayed': True}

        s.add(Event(
            id=eid,
            project_id=project_id,
            event_type=event_type,
            idempotency_key=x_github_delivery,
            payload=payload,
        ))
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()
            existing = (await s.execute(select(Event).where(
                Event.project_id == project_id,
                Event.idempotency_key == x_github_delivery,
            ))).scalar_one()
            return {'event_id': existing.id, 'status': existing.status, 'replayed': True}

    try:
        await enqueue({'id': eid, 'project_id': project_id, 'type': event_type, 'payload': payload, 'attempt': 1})
        async with SessionLocal() as s:
            await s.execute(update(Event).where(Event.id == eid).values(published_at=datetime.utcnow()))
            await s.commit()
    except Exception:
        pass

    return {'event_id': eid, 'status': 'queued', 'delivery_id': x_github_delivery}


@app.post('/v1/codeberg/rss')
async def codeberg_rss(request: Request, project_id: str = Depends(validate_api_key)):
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='RSS payload too large')
    try:
        events = parse_codeberg_rss(body.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(status_code=400, detail='invalid Codeberg RSS')

    accepted = []
    for item in events:
        async with SessionLocal() as s:
            existing = (await s.execute(select(Event).where(
                Event.project_id == project_id,
                Event.idempotency_key == item['idempotency_key'],
            ))).scalar_one_or_none()
            if existing:
                accepted.append({'event_id': existing.id, 'replayed': True})
                continue

            eid = 'evt_' + uuid.uuid4().hex
            s.add(Event(
                id=eid,
                project_id=project_id,
                event_type=item['type'],
                idempotency_key=item['idempotency_key'],
                payload=item['payload'],
            ))
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                existing = (await s.execute(select(Event).where(
                    Event.project_id == project_id,
                    Event.idempotency_key == item['idempotency_key'],
                ))).scalar_one()
                accepted.append({'event_id': existing.id, 'replayed': True})
                continue

        try:
            await enqueue({
                'id': eid,
                'project_id': project_id,
                'type': item['type'],
                'payload': item['payload'],
                'attempt': 1,
            })
            async with SessionLocal() as s:
                await s.execute(update(Event).where(Event.id == eid).values(
                    published_at=datetime.utcnow()
                ))
                await s.commit()
        except Exception:
            pass

        accepted.append({'event_id': eid, 'replayed': False})

    return {'accepted': len(accepted), 'events': accepted}


@app.post('/v1/events/{event_id}/replay')
async def replay_event(event_id: str, project_id: str = Depends(validate_api_key)):
    async with SessionLocal() as s:
        event = (await s.execute(select(Event).where(
            Event.id == event_id, Event.project_id == project_id
        ))).scalar_one_or_none()
        if not event:
            return {'error': 'not_found'}
        event.status = 'queued'
        event.last_error = None
        event.next_attempt_at = None
        event.dead_lettered_at = None
        await s.commit()
        payload = {'id': event.id, 'project_id': event.project_id, 'type': event.event_type, 'payload': event.payload, 'attempt': event.attempts + 1}

    await enqueue(payload)
    async with SessionLocal() as s:
        await s.execute(update(Event).where(Event.id == event_id).values(published_at=datetime.utcnow()))
        await s.commit()
    return {'event_id': event_id, 'status': 'queued', 'replayed': True}


@app.get('/v1/events/{event_id}')
async def get_event(event_id: str, project_id: str = Depends(validate_api_key)):
    async with SessionLocal() as s:
        e = (await s.execute(select(Event).where(
            Event.id == event_id, Event.project_id == project_id
        ))).scalar_one_or_none()
    if not e:
        return {'error': 'not_found'}
    return {
        'event_id': e.id,
        'type': e.event_type,
        'payload': e.payload,
        'status': e.status,
        'attempts': e.attempts,
        'last_error': e.last_error,
        'created_at': e.created_at,
        'updated_at': e.updated_at,
        'published_at': e.published_at,
        'delivered_at': e.delivered_at,
        'dead_lettered_at': e.dead_lettered_at,
    }


@app.websocket('/v1/ws')
async def ws(websocket: WebSocket, project_id: str = 'default-project'):
    await manager.connect(project_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(project_id, websocket)
