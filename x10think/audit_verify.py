from __future__ import annotations

import hashlib
import json
from pathlib import Path


def verify(path: str | Path) -> tuple[bool, int]:
    file_path = Path(path)
    if not file_path.exists():
        return True, 0
    previous = "0" * 64
    count = 0
    for line in file_path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        recorded = item.pop("hash", None)
        if item.get("prev_hash") != previous:
            return False, count
        canonical = json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode()).hexdigest()
        if recorded != expected:
            return False, count
        previous = recorded
        count += 1
    return True, count
