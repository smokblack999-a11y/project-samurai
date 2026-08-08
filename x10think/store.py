from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any


class Store:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "state.json"
        self.lock = Lock()

    def write(self, state: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        payload = json.dumps(state, ensure_ascii=False, indent=2)
        with self.lock:
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(self.path)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        with self.lock:
            return json.loads(self.path.read_text(encoding="utf-8"))
