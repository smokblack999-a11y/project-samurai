from __future__ import annotations

import os
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

HAMYLION_URL = os.getenv("HAMYLION_URL", "http://localhost:8000").rstrip("/")
HAMYLION_API_KEY = os.getenv("HAMYLION_API_KEY", "")

app = FastAPI(title="SAMURAI Core Bridge", version="1.0.0")


class EventIn(BaseModel):
    type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]
    idempotency_key: str | None = Field(default=None, max_length=255)
    module: str | None = Field(default=None, max_length=64)
    source: str | None = Field(default=None, max_length=64)
    schema_version: str = "1.0"


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"service": "samurai-core-bridge", "status": "ok", "hamylion_url": HAMYLION_URL}


@app.post("/v1/events")
async def publish(event: EventIn, x_api_key: str | None = Header(default=None)):
    key = x_api_key or HAMYLION_API_KEY
    if not key:
        raise HTTPException(500, "HAMYLION_API_KEY is not configured")

    idem = event.idempotency_key or f"samurai-{uuid.uuid4().hex}"
    payload = dict(event.payload)
    payload.update({
        "_samurai": {
            "module": event.module,
            "source": event.source,
            "schema_version": event.schema_version,
        }
    })

    body = {"type": event.type, "payload": payload, "idempotency_key": idem}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{HAMYLION_URL}/v1/events",
            json=body,
            headers={"X-API-Key": key},
        )

    if response.status_code >= 400:
        raise HTTPException(response.status_code, response.text[:1000])
    return response.json()
