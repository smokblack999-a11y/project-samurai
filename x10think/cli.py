from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import time
import uuid
from pathlib import Path
from typing import Any

from .operation import Operation, OperationStatus
from .report import report_json


def collect_telemetry() -> dict[str, Any]:
    root = Path.cwd()
    disk = shutil.disk_usage(root)
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cwd": str(root),
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
        "disk_used_ratio": round(disk.used / disk.total, 4) if disk.total else 0.0,
        "timestamp": time.time(),
    }


def build_local_report() -> dict[str, Any]:
    telemetry = collect_telemetry()
    disk_ok = telemetry["disk_total_bytes"] > 0 and telemetry["disk_free_bytes"] >= 0
    action = "health"
    payload = {"scope": "local"}
    operation = Operation(
        id=f"local-{uuid.uuid4().hex}",
        trace_id=f"trace-{uuid.uuid4().hex}",
        action=action,
        payload=payload,
        risk_score=5,
        fingerprint=Operation.make_fingerprint(action, payload),
        status=OperationStatus.VERIFIED if disk_ok else OperationStatus.VERIFY_FAILED,
        execution_id=None,
    )
    events = [
        {"event": "telemetry_collected", "data": telemetry},
        {"event": "health_verified", "data": {"disk_check": disk_ok}},
    ]
    return json.loads(report_json(operation, events))


def main() -> int:
    parser = argparse.ArgumentParser(prog="x10think", description="X10THINK Sentinel")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="collect local telemetry and produce an audit report")
    audit.add_argument("--output", default="x10think-report.json")
    args = parser.parse_args()

    if args.command == "audit":
        report = build_local_report()
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        print(f"X10THINK Sentinel report: {output.resolve()}")
        print(f"status={report['operation']['status']} risk={report['operation']['risk_score']}")
        return 0 if report["operation"]["status"] == OperationStatus.VERIFIED.value else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
