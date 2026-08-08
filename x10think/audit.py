from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock


class AuditLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def record(self, event: str, **data) -> dict:
        item = {"timestamp": time.time(), "event": event, "data": data}
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        return item
