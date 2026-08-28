from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass(frozen=True)
class IngestResult:
    accepted: bool
    duplicate: bool
    event_id: str | None
    reason: str | None = None

class NormalizedTelegramEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=200)
    chat_id: str = Field(min_length=1, max_length=100)
    message_id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)
    received_at: int
