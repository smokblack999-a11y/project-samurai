from __future__ import annotations

import json
from typing import Any


def build_report(operation: Any, audit_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic customer-facing JSON report from one Operation."""
    return {
        "report_version": "1.0",
        "operation": {
            "id": operation.id,
            "trace_id": operation.trace_id,
            "action": operation.action,
            "risk_score": operation.risk_score,
            "status": operation.status.value,
            "fingerprint": operation.fingerprint,
            "execution_id": operation.execution_id,
            "error": operation.error,
        },
        "audit": audit_items,
        "summary": {
            "audit_events": len(audit_items),
            "integrity_claim": "hash-chain audit events included",
        },
    }


def report_json(operation: Any, audit_items: list[dict[str, Any]]) -> str:
    return json.dumps(build_report(operation, audit_items), ensure_ascii=False, indent=2, sort_keys=True)
