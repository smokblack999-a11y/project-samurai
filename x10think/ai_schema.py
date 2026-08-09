from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class AIAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(max_length=2000)
    severity: Literal["info", "low", "medium", "high", "critical"]
    findings: list[str] = Field(default_factory=list, max_length=20)
    next_steps: list[str] = Field(default_factory=list, max_length=20)
