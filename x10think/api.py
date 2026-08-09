from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core import health, load_config, safe_action
from ai import analyze

BASE = Path(__file__).resolve().parent
CONFIG = load_config()
app = FastAPI(title="X10THINK Sentinel API", version=CONFIG.get("version", "0.2.0"))


class AnalyzeRequest(BaseModel):
    payload: dict = Field(default_factory=dict)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE / "dashboard.html")


@app.get("/status")
def status():
    h = health()
    return {"agent": "online", "version": CONFIG.get("version"), "health": h["score"]}


@app.get("/system/status")
def system_status():
    """Single machine-readable status surface for the dashboard."""
    h = health()
    return {
        "service": {"name": CONFIG.get("name"), "version": CONFIG.get("version"), "pid": os.getpid()},
        "health": h,
        "ai": {
            "provider_mode": os.getenv("X10_AI_PROVIDER", CONFIG.get("ai_provider", "auto")),
            "together_configured": bool(os.getenv("TOGETHER_API_KEY")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        },
    }


@app.get("/health")
def health_route():
    return health()


@app.post("/scan")
def scan():
    h = health()
    return {"health": h, "ai": analyze(h)}


@app.post("/action")
def action(name: str):
    result = safe_action(name)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/analyze")
def analyze_route(req: AnalyzeRequest):
    return analyze(req.payload)
