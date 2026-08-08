from __future__ import annotations

import os
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class HealthSnapshot:
    timestamp: float
    load_1m: float | None
    disk_free_pct: float
    memory_available_mb: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _memory_available_mb() -> float | None:
    try:
        values = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0])
        return round(values["MemAvailable"] / 1024, 1)
    except (OSError, KeyError, ValueError):
        return None


def snapshot(path: str | Path = "/") -> HealthSnapshot:
    total, used, free = shutil.disk_usage(path)
    disk_free_pct = round((free / total) * 100, 2) if total else 0.0
    load = None
    try:
        load = round(os.getloadavg()[0], 2)
    except (AttributeError, OSError):
        pass
    return HealthSnapshot(time.time(), load, disk_free_pct, _memory_available_mb())


def score(s: HealthSnapshot) -> int:
    points = 100
    if s.disk_free_pct < 10:
        points -= 35
    elif s.disk_free_pct < 20:
        points -= 15
    if s.memory_available_mb is not None and s.memory_available_mb < 256:
        points -= 25
    if s.load_1m is not None and s.load_1m > 4:
        points -= 15
    return max(0, min(100, points))
