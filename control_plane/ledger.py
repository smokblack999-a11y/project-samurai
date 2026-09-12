from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from .models import ActionEnvelope, DecisionRecord, utc_now


class AuditLedger:
    """Append-only JSONL ledger for local MVPs. Production should move this boundary to PostgreSQL."""

    def __init__(self, path: str = "data/control_plane_audit.jsonl") -> None:
        self.path = Path(path)
        self._lock = Lock()

    def append(self, action: ActionEnvelope, decision: DecisionRecord, result: dict[str, Any] | None = None) -> None:
        event = {
            "timestamp": utc_now(),
            "action": action.to_dict(),
            "decision": decision.to_dict(),
            "result": result,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
