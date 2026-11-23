from __future__ import annotations
from collections import defaultdict, deque
from time import monotonic

class RateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self.hits = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        q = self.hits[key]
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
