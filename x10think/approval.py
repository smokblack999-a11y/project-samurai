from __future__ import annotations

import time
import uuid
from typing import Any

from audit import AuditLog
from policy import evaluate

AUDIT = AuditLog("logs/audit.jsonl")
_APPROVALS: dict[str, dict[str, Any]] = {}


def create(action: str, payload: dict | None = None, requested_by: str = "assistant") -> dict:
    decision = evaluate(action)
    if not decision.allowed:
        AUDIT.record("action_blocked", action=action, requested_by=requested_by, reason=decision.reason)
        raise ValueError("action_forbidden")
    approval_id = str(uuid.uuid4())
    item = {
        "id": approval_id,
        "action": action,
        "classification": decision.classification.value,
        "requires_approval": decision.requires_approval,
        "payload": payload or {},
        "requested_by": requested_by,
        "status": "pending" if decision.requires_approval else "approved",
        "created_at": time.time(),
    }
    _APPROVALS[approval_id] = item
    AUDIT.record("approval_created", approval_id=approval_id, action=action, requested_by=requested_by)
    return item.copy()


def get(approval_id: str) -> dict | None:
    item = _APPROVALS.get(approval_id)
    return item.copy() if item else None


def decide(approval_id: str, decision: str, comment: str | None = None, role: str = "operator") -> dict | None:
    item = _APPROVALS.get(approval_id)
    if not item:
        return None
    if item["status"] != "pending":
        return item.copy()
    if role not in {"operator", "admin"}:
        raise ValueError("approval_permission_denied")
    if decision not in {"approve", "reject"}:
        raise ValueError("invalid_decision")
    item["status"] = "approved" if decision == "approve" else "rejected"
    item["comment"] = comment
    item["decided_at"] = time.time()
    AUDIT.record("approval_decided", approval_id=approval_id, action=item["action"], decision=decision, role=role)
    return item.copy()


def list_pending() -> list[dict]:
    return [item.copy() for item in _APPROVALS.values() if item["status"] == "pending"]
