from __future__ import annotations

from audit import AuditLog
from approval import get, mark_executed
from policy import evaluate

AUDIT = AuditLog("logs/audit.jsonl")


def execute_approved(approval_id: str) -> dict:
    item = get(approval_id)
    if not item:
        raise ValueError("approval_not_found")
    if item["status"] == "executed":
        AUDIT.record("execution_replayed", approval_id=approval_id, action=item["action"])
        raise ValueError("already_executed")
    if item["status"] != "approved":
        raise ValueError("approval_required")

    decision = evaluate(item["action"])
    if not decision.allowed:
        AUDIT.record("execution_blocked", approval_id=approval_id, action=item["action"])
        raise ValueError("action_forbidden")

    if item["action"] == "health":
        from core import health
        result = health()
    elif item["action"] == "disk_report":
        from core import disk_report
        result = disk_report()
    else:
        raise ValueError("executor_not_implemented")

    if not mark_executed(approval_id):
        raise ValueError("execution_state_conflict")
    AUDIT.record("execution_completed", approval_id=approval_id, action=item["action"], fingerprint=item["fingerprint"])
    return {"approval_id": approval_id, "action": item["action"], "result": result}
