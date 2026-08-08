from __future__ import annotations

from audit import AuditLog
from approval import get
from policy import evaluate

AUDIT = AuditLog("logs/audit.jsonl")


def execute_approved(approval_id: str) -> dict:
    item = get(approval_id)
    if not item:
        raise ValueError("approval_not_found")
    if item["status"] != "approved":
        raise ValueError("approval_required")

    decision = evaluate(item["action"])
    if not decision.allowed:
        AUDIT.record("execution_blocked", approval_id=approval_id, action=item["action"])
        raise ValueError("action_forbidden")

    # v0.2 executes only read-only actions. Mutating actions require a
    # dedicated executor implementation instead of arbitrary shell access.
    if item["action"] == "health":
        from core import health
        result = health()
    elif item["action"] == "disk_report":
        from core import disk_report
        result = disk_report()
    else:
        raise ValueError("executor_not_implemented")

    AUDIT.record("execution_completed", approval_id=approval_id, action=item["action"])
    return {"approval_id": approval_id, "action": item["action"], "result": result}
