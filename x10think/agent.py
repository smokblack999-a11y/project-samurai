from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from .health import score, snapshot
from .security import scan
from .store import Store


class Agent:
    def __init__(self, data_dir: Path):
        self.store = Store(data_dir)

    def scan_once(self) -> dict:
        health = snapshot()
        findings = scan(".")
        state = {
            "agent": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health": health.to_dict(),
            "score": score(health),
            "security": findings,
        }
        self.store.write(state)
        return state

    def run_forever(self, interval: int) -> None:
        while True:
            self.scan_once()
            time.sleep(interval)
