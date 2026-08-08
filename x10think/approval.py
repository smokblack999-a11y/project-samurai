from __future__ import annotations

import time
import uuid
from typing import Any

SAFE_ACTIONS = {
    "health": "Read current health telemetry",
    "disk_report": "Read disk usage",
}

_APPROVALS: dict[str, dict[str, Any]] = {}


def create(action: str, payload: dict | None = None, requested_by: str = "assistant") -> dict:
    if action not in SAFE_ACTIONS:
        raise ValueError("action_not_allowlisted")
    approval_id = str(uuid.uuid4())
    item = {
        "id": approval_id,
        "action": action,
        "payload": payload or {},
        "requested_by": requested_by,
        "status": "pending",
        "created_at": time.time(),
    }
    _APPROVALS[approval_id] = item
    return item.copy()


def get(approval_id: str) -> dict | None:
    item = _APPROVALS.get(approval_id)
    return item.copy() if item else None


def decide(approval_id: str, decision: str, comment: str | None = None) -> dict | None:
    item = _APPROVALS.get(approval_id)
    if not item:
        return None
    if item["status"] != "pending":
        return item.copy()
    if decision not in {"approve", "reject"}:
        raise ValueError("invalid_decision")
    item["status"] = "approved" if decision == "approve" else "rejected"
    item["comment"] = comment
    item["decided_at"] = time.time()
    return item.copy()


def list_pending() -> list[dict]:
    return [item.copy() for item in _APPROVALS.values() if item["status"] == "pending"]
