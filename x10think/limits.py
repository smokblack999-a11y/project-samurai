from __future__ import annotations

import os
import time
from collections import defaultdict
from threading import Lock

WINDOW_SECONDS = 60
MAX_REQUESTS = int(os.getenv("X10_MAX_REQUESTS_PER_MINUTE", "60"))
MAX_AI_CALLS = int(os.getenv("X10_MAX_AI_CALLS_PER_MINUTE", "10"))

_lock = Lock()
_requests: dict[str, list[float]] = defaultdict(list)
_ai_calls: dict[str, list[float]] = defaultdict(list)


def _allow(bucket: dict[str, list[float]], key: str, limit: int) -> bool:
    now = time.time()
    with _lock:
        values = [t for t in bucket[key] if now - t < WINDOW_SECONDS]
        if len(values) >= limit:
            bucket[key] = values
            return False
        values.append(now)
        bucket[key] = values
        return True


def allow_request(key: str) -> bool:
    return _allow(_requests, key, MAX_REQUESTS)


def allow_ai(key: str) -> bool:
    return _allow(_ai_calls, key, MAX_AI_CALLS)
