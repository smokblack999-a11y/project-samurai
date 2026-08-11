from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class IngestResult:
    accepted: bool
    duplicate: bool
    event_id: str | None
    reason: str | None = None
