from __future__ import annotations

from pydantic import BaseModel, Field


class Finding(BaseModel):
    title: str = Field(max_length=200)
    severity: str = Field(pattern="^(info|low|medium|high|critical)$")
    evidence: str = Field(max_length=1000)


class AIAnalysis(BaseModel):
    summary: str = Field(max_length=2000)
    severity: str = Field(pattern="^(info|low|medium|high|critical)$")
    findings: list[Finding] = Field(default_factory=list, max_length=20)
    next_steps: list[str] = Field(default_factory=list, max_length=20)
