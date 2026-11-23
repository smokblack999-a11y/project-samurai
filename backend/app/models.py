from pydantic import BaseModel, Field
from typing import Literal

Intent = Literal["buying", "question", "support", "spam", "other"]
Urgency = Literal["low", "medium", "high"]
Action = Literal["human_followup", "reply", "ignore", "escalate"]

class AnalyzeMessageRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=128)
    chat_id: str | None = None
    text: str = Field(min_length=1, max_length=10000)
    language_hint: str | None = None

class LeadDecision(BaseModel):
    message_id: str
    intent: Intent
    lead_score: int = Field(ge=0, le=100)
    urgency: Urgency
    language: str
    needs: list[str]
    recommended_action: Action
    reason: str
