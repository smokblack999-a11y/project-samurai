from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import time
from pathlib import Path

from .audit import AuditLog
from .operation import Operation, OperationStatus
from .report import report_json


def collect_telemetry() -> dict:
    total, used, free = shutil.disk_usage(Path.home())
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "disk_total_bytes": total,
        "disk_used_bytes": used,
        "disk_free_bytes": free,
        "timestamp": time.time(),
    }


def build_operation(telemetry: dict) -> Operation:
    free_ratio = telemetry["disk_free_bytes"] / max(telemetry["disk_total_bytes"], 1)
    risk = 85 if free_ratio < 0.05 else 55 if free_ratio < 0.15 else 15
    action = "write_report" if risk >= 55 else "health"
    payload = {"hostname": telemetry["hostname"], "reason": "sentinel_audit"}
    return Operation(
        id=f"audit-{int(time.time())}",
        trace_id=f"trace-{int(time.time_ns())}",
        action=action,
        payload=payload,
        risk_score=risk,
        fingerprint=Operation.make_fingerprint(action, payload),
        status=OperationStatus.VERIFIED,
    )


def run_audit(output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    telemetry = collect_telemetry()
    operation = build_operation(telemetry)
    audit = AuditLog(output.with_suffix(".audit.jsonl"))
    audit_items = [audit.record("telemetry_collected", telemetry=telemetry)]
    audit_items.append(audit.record("operation_verified", operation_id=operation.id, risk_score=operation.risk_score))
    output.write_text(report_json(operation, audit_items), encoding="utf-8")
    print(json.dumps({"status": "ok", "report": str(output), "risk_score": operation.risk_score}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="x10think-sentinel")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="collect local telemetry and write a Sentinel report")
    audit.add_argument("--output", default="x10think-report.json")
    args = parser.parse_args()
    if args.command == "audit":
        return run_audit(Path(args.output))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
