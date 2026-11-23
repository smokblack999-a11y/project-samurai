from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core import Event, IncidentStore

app = FastAPI(title="SAMURAI SENTINEL X", version="0.1.0")
store = IncidentStore()


class EventInput(BaseModel):
    source: str = "unknown"
    kind: str
    host: str
    timestamp: str | None = None
    severity: int = Field(default=0, ge=0, le=100)
    confidence: float = Field(default=0.5, ge=0, le=1)
    process: str | None = None
    parent_process: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    remote_ip: str | None = None
    user: str | None = None
    tags: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sentinel-x"}


@app.post("/events")
def ingest(payload: EventInput) -> dict:
    data = payload.model_dump(exclude_none=True)
    return store.ingest(Event.from_dict(data)).as_dict()


@app.get("/incidents")
def incidents() -> list[dict]:
    return [i.as_dict() for i in store.list()]


@app.get("/incidents/{incident_id}")
def incident(incident_id: str) -> dict:
    item = store.get(incident_id)
    if item is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return item.as_dict()
