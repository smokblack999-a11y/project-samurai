from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class LeadDecision(BaseModel):
    intent: str
    lead_score: int = Field(ge=0, le=100)
    urgency: str
    recommended_action: str
    needs: list[str] = Field(default_factory=list, max_length=20)
    reason: str = Field(min_length=1, max_length=2000)

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        if value not in {"buying", "information"}:
            raise ValueError("invalid intent")
        return value

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, value: str) -> str:
        if value not in {"high", "low"}:
            raise ValueError("invalid urgency")
        return value

    @field_validator("recommended_action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        if value not in {"human_followup", "auto_reply"}:
            raise ValueError("invalid recommended_action")
        return value


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str | None = Field(default=None, max_length=20)


class NormalizedMessage(BaseModel):
    source: str = "telegram"
    account_id: str = Field(min_length=1, max_length=100)
    chat_id: str = Field(min_length=1, max_length=100)
    message_id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)
    received_at: int
