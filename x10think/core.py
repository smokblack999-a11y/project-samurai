from __future__ import annotations

import json
import os
import platform
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
STARTED_AT = time.time()


@dataclass
class Snapshot:
    timestamp: float
    platform: str
    python: str
    hostname: str
    disk_free_pct: float
    load_1m: float | None
    memory_available_pct: float | None


def load_config() -> dict:
    with (BASE / "config.json").open(encoding="utf-8") as f:
        return json.load(f)


def _memory_available_pct() -> float | None:
    try:
        values: dict[str, float] = {}
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                key, value = line.split(":", 1)
                values[key] = float(value.strip().split()[0])
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        return round((available / total) * 100, 2) if total and available is not None else None
    except (OSError, ValueError):
        return None


def snapshot() -> Snapshot:
    usage = shutil.disk_usage(BASE)
    free_pct = (usage.free / usage.total) * 100 if usage.total else 0.0
    try:
        load = os.getloadavg()[0]
    except (AttributeError, OSError):
        load = None
    return Snapshot(
        timestamp=time.time(),
        platform=platform.system(),
        python=f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
        hostname=platform.node(),
        disk_free_pct=round(free_pct, 2),
        load_1m=round(load, 2) if load is not None else None,
        memory_available_pct=_memory_available_pct(),
    )


def health() -> dict:
    s = snapshot()
    cfg = load_config()
    thresholds = cfg.get("thresholds", {})
    disk_critical = float(thresholds.get("disk_critical_pct", 10))
    disk_warning = float(thresholds.get("disk_warning_pct", 20))
    load_warning = float(thresholds.get("load_warning", 4))

    score = 100
    findings = []
    if s.disk_free_pct < disk_critical:
        score -= 35
        findings.append({"severity": "high", "id": "disk-low", "message": f"Less than {disk_critical:g}% disk space remains."})
    elif s.disk_free_pct < disk_warning:
        score -= 15
        findings.append({"severity": "medium", "id": "disk-warning", "message": f"Less than {disk_warning:g}% disk space remains."})
    if s.load_1m is not None and s.load_1m > load_warning:
        score -= 15
        findings.append({"severity": "medium", "id": "load-high", "message": "1-minute system load is high."})
    if s.memory_available_pct is not None and s.memory_available_pct < 10:
        score -= 20
        findings.append({"severity": "high", "id": "memory-low", "message": "Less than 10% memory is available."})

    return {
        "score": max(score, 0),
        "snapshot": asdict(s),
        "findings": findings,
        "uptime_seconds": round(time.time() - STARTED_AT, 2),
    }


def safe_action(action: str) -> dict:
    """Allow-list only. No arbitrary shell execution."""
    if action == "health":
        return {"ok": True, "result": health()}
    if action == "disk_report":
        usage = shutil.disk_usage(BASE)
        return {"ok": True, "result": {"total": usage.total, "free": usage.free, "used": usage.used}}
    return {"ok": False, "error": "Action is not allow-listed."}
