from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import health, safe_action
from ai import analyze
from approval import create as create_approval, get as get_approval, decide as decide_approval, list_pending
from executor import execute_approved

BASE = Path(__file__).resolve().parent
app = FastAPI(title="X10THINK Sentinel API", version="0.3.0")

class AnalyzeRequest(BaseModel):
    payload: dict

class ApprovalRequest(BaseModel):
    action: str
    payload: dict = {}
    requested_by: str = "assistant"

class DecisionRequest(BaseModel):
    decision: str
    comment: str | None = None
    role: str = "operator"

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE / "dashboard.html")

@app.get("/status")
def status():
    h = health()
    return {"agent": "online", "version": "0.3.0", "health": h["score"]}

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

@app.post("/approvals")
def approvals_create(req: ApprovalRequest):
    try:
        return create_approval(req.action, req.payload, req.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/approvals")
def approvals_pending():
    return {"items": list_pending()}

@app.get("/approvals/{approval_id}")
def approvals_get(approval_id: str):
    item = get_approval(approval_id)
    if not item:
        raise HTTPException(status_code=404, detail="approval_not_found")
    return item

@app.post("/approvals/{approval_id}/decision")
def approvals_decide(approval_id: str, req: DecisionRequest):
    try:
        item = decide_approval(approval_id, req.decision, req.comment, req.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not item:
        raise HTTPException(status_code=404, detail="approval_not_found")
    return item

@app.post("/approvals/{approval_id}/execute")
def approvals_execute(approval_id: str):
    try:
        return execute_approved(approval_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
