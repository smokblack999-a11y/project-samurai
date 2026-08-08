from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    app_name: str = "X10THINK Sentinel"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 7010
    interval: int = 10
    data_dir: Path = Path(".x10think")

    @classmethod
    def load(cls, path: str | Path = "x10think.json") -> "Settings":
        raw: dict[str, Any] = {}
        config_path = Path(path)
        if config_path.exists():
            raw = json.loads(config_path.read_text(encoding="utf-8"))

        data_dir = Path(os.getenv("X10_DATA_DIR", raw.get("data_dir", ".x10think")))
        return cls(
            app_name=raw.get("app_name", cls.app_name),
            version=raw.get("version", cls.version),
            host=os.getenv("X10_HOST", raw.get("host", cls.host)),
            port=int(os.getenv("X10_PORT", raw.get("port", cls.port))),
            interval=max(2, int(raw.get("interval", cls.interval))),
            data_dir=data_dir,
        )
