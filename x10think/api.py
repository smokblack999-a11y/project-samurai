from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import health, safe_action
from ai import analyze

BASE = Path(__file__).resolve().parent
app = FastAPI(title="X10THINK Sentinel API", version="0.1.0")

class AnalyzeRequest(BaseModel):
    payload: dict

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE / "dashboard.html")

@app.get("/status")
def status():
    h = health()
    return {"agent": "online", "version": "0.1.0", "health": h["score"]}

@app.get("/health")
def health_route():
    return health()

@app.post("/scan")
def scan():
    h = health()
    return {"health": h, "ai": analyze(h)}

@app.post("/action")
def action(name: str):
    return safe_action(name)

@app.post("/analyze")
def analyze_route(req: AnalyzeRequest):
    return analyze(req.payload)
