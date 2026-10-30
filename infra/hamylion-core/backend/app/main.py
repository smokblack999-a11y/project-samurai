import uuid
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import SessionLocal, engine
from .models import Base, Event
from .schemas import EventRequest, EventResponse
from .auth import validate_api_key
from .config import settings
from .queue import enqueue
from .websocket import manager

app = FastAPI(title="HAMYLION Core", version="3.0.0")


@app.on_event("startup")
async def startup():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "hamylion-core", "version": "3.0.0"}


@app.post("/v1/events", response_model=EventResponse)
async def create_event(
    req: EventRequest,
    project_id: str = Depends(validate_api_key),
):
    async with SessionLocal() as session:
        existing = (
            await session.execute(
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

        event_id = "evt_" + uuid.uuid4().hex
        event = Event(
            id=event_id,
            project_id=project_id,
            event_type=req.type,
            idempotency_key=req.idempotency_key,
            payload=req.payload,
        )
        session.add(event)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            existing = (
                await session.execute(
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

    await enqueue(
        {
            "id": event_id,
            "project_id": project_id,
            "type": req.type,
            "payload": req.payload,
        }
    )
    return EventResponse(event_id=event_id, status="queued")


@app.get("/v1/events/{event_id}")
async def get_event(
    event_id: str,
    project_id: str = Depends(validate_api_key),
):
    async with SessionLocal() as session:
        event = (
            await session.execute(
                select(Event).where(
                    Event.id == event_id,
                    Event.project_id == project_id,
                )
            )
        ).scalar_one_or_none()

    if event is None:
        return {"error": "not_found"}

    return {
        "event_id": event.id,
        "type": event.event_type,
        "payload": event.payload,
        "status": event.status,
        "attempts": event.attempts,
        "last_error": event.last_error,
        "created_at": event.created_at,
        "delivered_at": event.delivered_at,
    }


@app.websocket("/v1/ws")
async def ws(websocket: WebSocket):
    # WebSocket routes do not inherit the HTTP endpoint's Depends(validate_api_key).
    # Authenticate explicitly before accepting the connection.
    configured_key = settings.API_KEY
    supplied_key = websocket.headers.get("x-api-key")

    if not configured_key:
        await websocket.close(code=1011, reason="API authentication is not configured")
        return
    if supplied_key != configured_key:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Current auth implementation maps all valid API keys to this one project.
    # Do not allow clients to choose an arbitrary project_id via query parameters.
    project_id = "default-project"
    await manager.connect(project_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(project_id, websocket)
