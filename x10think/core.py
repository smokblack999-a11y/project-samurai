from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path

BASE = Path(__file__).resolve().parent

@dataclass
class Snapshot:
    timestamp: float
    platform: str
    python: str
    disk_free_pct: float
    load_1m: float | None


def load_config() -> dict:
    with (BASE / "config.json").open(encoding="utf-8") as f:
        return json.load(f)


def snapshot() -> Snapshot:
    usage = shutil.disk_usage(BASE)
    free_pct = (usage.free / usage.total) * 100 if usage.total else 0.0
    load = None
    try:
        load = os.getloadavg()[0]
    except (AttributeError, OSError):
        pass
    return Snapshot(time.time(), os.name, f"{os.sys.version_info.major}.{os.sys.version_info.minor}", round(free_pct, 2), load)


def health() -> dict:
    s = snapshot()
    score = 100
    findings = []
    if s.disk_free_pct < 10:
        score -= 35
        findings.append({"severity": "high", "id": "disk-low", "message": "Less than 10% disk space remains."})
    elif s.disk_free_pct < 20:
        score -= 15
        findings.append({"severity": "medium", "id": "disk-warning", "message": "Less than 20% disk space remains."})
    if s.load_1m is not None and s.load_1m > 4:
        score -= 15
        findings.append({"severity": "medium", "id": "load-high", "message": "1-minute system load is high."})
    return {"score": max(score, 0), "snapshot": asdict(s), "findings": findings}


def safe_action(action: str) -> dict:
    """Allow-list only. No arbitrary shell execution."""
    if action == "health":
        return {"ok": True, "result": health()}
    if action == "disk_report":
        usage = shutil.disk_usage(BASE)
        return {"ok": True, "result": {"total": usage.total, "free": usage.free, "used": usage.used}}
    return {"ok": False, "error": "Action is not allow-listed."}
