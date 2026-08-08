from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time


def approval_fingerprint(action: str, payload: dict) -> str:
    canonical = json.dumps({"action": action, "payload": payload}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


def new_secret() -> str:
    return secrets.token_urlsafe(32)


def approval_ttl() -> int:
    try:
        return max(30, min(int(os.getenv("X10_APPROVAL_TTL", "300")), 3600))
    except ValueError:
        return 300


def now() -> float:
    return time.time()
