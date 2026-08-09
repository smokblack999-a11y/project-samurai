from __future__ import annotations

import json
import os
from typing import Literal

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel, Field

app = FastAPI(title="Telegram LeadOps AI", version="0.1.0")

class Message(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

class Decision(BaseModel):
    intent: Literal["buying", "information"]
    lead_score: int = Field(ge=0, le=100)
    urgency: Literal["low", "high"]
    recommended_action: Literal["human_followup", "auto_reply"]
    needs: list[str] = Field(default_factory=list, max_length=20)
    reason: str = Field(min_length=1, max_length=1000)


def baseline(text: str) -> Decision:
    t = text.casefold()
    buying = any(x in t for x in ("купить", "цена", "стоимость", "заказать", "оплатить", "buy", "price", "order"))
    urgent = any(x in t for x in ("сегодня", "срочно", "сейчас", "today", "urgent", "now"))
    needs = []
    if any(x in t for x in ("цена", "стоимость", "price", "cost")): needs.append("price")
    if any(x in t for x in ("есть", "свободно", "доступно", "можно", "available")): needs.append("availability")
    score = min(100, (78 if buying else 28) + (12 if urgent else 0))
    return Decision(intent="buying" if buying else "information", lead_score=score, urgency="high" if urgent else "low", recommended_action="human_followup" if buying else "auto_reply", needs=needs, reason="deterministic baseline")


def analyze(text: str) -> Decision:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return baseline(text)
    try:
        client = OpenAI(timeout=12, max_retries=1)
        r = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            instructions="Classify this inbound business message. Return JSON only: intent (buying/information), lead_score 0..100, urgency (low/high), recommended_action (human_followup/auto_reply), needs array, reason. Do not invent facts.",
            input=text,
        )
        return Decision.model_validate(json.loads(r.output_text))
    except Exception:
        return baseline(text)

@app.get("/health")
def health():
    return {"status": "ok", "service": "telegram-leadops", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/v1/analyze/message", response_model=Decision)
def analyze_message(message: Message):
    return analyze(message.text)
