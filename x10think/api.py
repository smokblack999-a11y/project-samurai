from __future__ import annotations

from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ai import analyze
from approval import create as create_approval, decide as decide_approval, get as get_approval, list_pending
from auth import operator_role, viewer_role
from core import health, safe_action
from executor import execute_approved

BASE = Path(__file__).resolve().parent
app = FastAPI(title="X10THINK Sentinel API", version="0.4.0")


class AnalyzeRequest(BaseModel):
    payload: dict


class ApprovalRequest(BaseModel):
    action: str
    payload: dict = Field(default_factory=dict)
    requested_by: str = "assistant"


class DecisionRequest(BaseModel):
    decision: str
    comment: str | None = None


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE / "dashboard.html")


@app.get("/status")
def status():
    h = health()
    return {"agent": "online", "version": "0.4.0", "health": h["score"]}


@app.get("/health")
def health_route():
    return health()


@app.post("/scan")
def scan(_: str = Depends(viewer_role)):
    h = health()
    return {"health": h, "ai": analyze(h)}


@app.post("/action")
def action(name: str, _: str = Depends(operator_role)):
    return safe_action(name)


@app.post("/analyze")
def analyze_route(req: AnalyzeRequest, _: str = Depends(viewer_role)):
    return analyze(req.payload)


@app.post("/approvals")
def approvals_create(req: ApprovalRequest, _: str = Depends(viewer_role)):
    try:
        return create_approval(req.action, req.payload, req.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/approvals")
def approvals_pending(_: str = Depends(viewer_role)):
    return {"items": list_pending()}


@app.get("/approvals/{approval_id}")
def approvals_get(approval_id: str, _: str = Depends(viewer_role)):
    item = get_approval(approval_id)
    if not item:
        raise HTTPException(status_code=404, detail="approval_not_found")
    return item


@app.post("/approvals/{approval_id}/decision")
def approvals_decide(approval_id: str, req: DecisionRequest, role: str = Depends(operator_role)):
    try:
        item = decide_approval(approval_id, req.decision, req.comment, role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not item:
        raise HTTPException(status_code=404, detail="approval_not_found")
    return item


@app.post("/approvals/{approval_id}/execute")
def approvals_execute(approval_id: str, _: str = Depends(operator_role)):
    try:
        return execute_approved(approval_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
