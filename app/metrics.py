from __future__ import annotations

from collections import Counter
from threading import Lock


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counts = Counter()

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counts[name] += value

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)


metrics = Metrics()
