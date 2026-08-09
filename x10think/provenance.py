from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def proposal_fingerprint(proposal: dict[str, Any], source: dict[str, Any]) -> str:
    body = {"proposal": proposal, "source": source}
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
