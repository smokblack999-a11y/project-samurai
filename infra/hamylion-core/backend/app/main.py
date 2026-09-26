import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from .auth import validate_api_key
from .db import SessionLocal, engine
from .models import Base, Event
from .queue import enqueue
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
        existing = (
            await s.execute(
                select(Event).where(
                    Event.project_id == project_id,
                    Event.idempotency_key == req.idempotency_key,
                )
            )
        ).scalar_one_or_none()
        if existing:
            return EventResponse(
                event_id=existing.id,
                status=existing.status,
                replayed=True,
            )

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
            existing = (
                await s.execute(
                    select(Event).where(
                        Event.project_id == project_id,
                        Event.idempotency_key == req.idempotency_key,
                    )
                )
            ).scalar_one()
            return EventResponse(
                event_id=existing.id,
                status=existing.status,
                replayed=True,
            )

    try:
        await enqueue({'id': eid, 'project_id': project_id, 'type': req.type, 'payload': req.payload, 'attempt': 1})
        async with SessionLocal() as s:
            await s.execute(update(Event).where(Event.id == eid).values(published_at=datetime.utcnow()))
            await s.commit()
    except Exception:
        # The durable DB record remains queued; the worker can recover publication.
        pass

    return EventResponse(event_id=eid, status='queued')


@app.post('/v1/events/{event_id}/replay')
async def replay_event(event_id: str, project_id: str = Depends(validate_api_key)):
    async with SessionLocal() as s:
        event = (
            await s.execute(
                select(Event).where(Event.id == event_id, Event.project_id == project_id)
            )
        ).scalar_one_or_none()
        if not event:
            return {'error': 'not_found'}
        event.status = 'queued'
        event.last_error = None
        event.next_attempt_at = None
        event.dead_lettered_at = None
        await s.commit()
        payload = {
            'id': event.id,
            'project_id': event.project_id,
            'type': event.event_type,
            'payload': event.payload,
            'attempt': event.attempts + 1,
        }

    await enqueue(payload)
    async with SessionLocal() as s:
        await s.execute(update(Event).where(Event.id == event_id).values(published_at=datetime.utcnow()))
        await s.commit()
    return {'event_id': event_id, 'status': 'queued', 'replayed': True}


@app.get('/v1/events/{event_id}')
async def get_event(event_id: str, project_id: str = Depends(validate_api_key)):
    async with SessionLocal() as s:
        e = (
            await s.execute(
                select(Event).where(Event.id == event_id, Event.project_id == project_id)
            )
        ).scalar_one_or_none()
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
