from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from threading import Lock
from typing import Any


class AuditLog:
    """Append-only hash chained audit storage."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._last_hash = self._recover_last_hash()

    def _recover_last_hash(self) -> str:
        if not self.path.exists():
            return "0" * 64
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
            return json.loads(lines[-1]).get("hash", "0" * 64) if lines else "0" * 64
        except Exception:
            return "0" * 64

    def record(
        self,
        event: str,
        operation_id: str | None = None,
        trace_id: str | None = None,
        **data: Any,
    ) -> dict:
        with self._lock:
            item = {
                "timestamp": time.time(),
                "event": event,
                "operation_id": operation_id,
                "trace_id": trace_id,
                "data": data,
                "prev_hash": self._last_hash,
            }
            canonical = json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            item["hash"] = hashlib.sha256(canonical.encode()).hexdigest()
            self._last_hash = item["hash"]
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            return item

    def verify_chain(self) -> bool:
        previous = "0" * 64
        if not self.path.exists():
            return True
        for line in self.path.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            saved_hash = item.pop("hash")
            if item.get("prev_hash") != previous:
                return False
            canonical = json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            if hashlib.sha256(canonical.encode()).hexdigest() != saved_hash:
                return False
            previous = saved_hash
        return True
