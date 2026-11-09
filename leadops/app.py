from __future__ import annotations

import json
import os
from typing import Literal

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel, Field

from telegram_adapter import normalize_update
from store import EventStore

app = FastAPI(title="Telegram LeadOps AI", version="0.2.0")
store = EventStore(os.getenv("LEADOPS_DB", "leadops.db"))

class Message(BaseModel):
    message_id: str = Field(min_length=1, max_length=128)
    chat_id: str | None = None
    text: str = Field(min_length=1, max_length=10000)

class Decision(BaseModel):
    message_id: str
    intent: Literal["buying", "information"]
    lead_score: int = Field(ge=0, le=100)
    urgency: Literal["low", "high"]
    recommended_action: Literal["human_followup", "auto_reply"]
    needs: list[str] = Field(default_factory=list, max_length=20)
    reason: str = Field(min_length=1, max_length=1000)

class TelegramUpdate(BaseModel):
    update: dict


def baseline(message: Message) -> Decision:
    t = message.text.casefold()
    buying = any(x in t for x in ("купить", "цена", "стоимость", "заказать", "оплатить", "buy", "price", "order"))
    urgent = any(x in t for x in ("сегодня", "срочно", "сейчас", "today", "urgent", "now"))
    needs: list[str] = []
    if any(x in t for x in ("цена", "стоимость", "price", "cost")): needs.append("price")
    if any(x in t for x in ("есть", "свободно", "доступно", "можно", "available")): needs.append("availability")
    score = min(100, (78 if buying else 28) + (12 if urgent else 0))
    return Decision(message_id=message.message_id, intent="buying" if buying else "information", lead_score=score, urgency="high" if urgent else "low", recommended_action="human_followup" if buying else "auto_reply", needs=needs, reason="deterministic baseline")


def analyze(message: Message) -> Decision:
    if not os.getenv("OPENAI_API_KEY"):
        return baseline(message)
    try:
        client = OpenAI(timeout=12, max_retries=1)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            instructions="Classify this inbound business message. Return JSON only: intent (buying/information), lead_score 0..100, urgency (low/high), recommended_action (human_followup/auto_reply), needs array, reason. Do not invent facts.",
            input=message.text,
        )
        return Decision.model_validate({"message_id": message.message_id, **json.loads(response.output_text)})
    except Exception:
        return baseline(message)

@app.get("/health")
def health():
    return {"status": "ok", "service": "telegram-leadops", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/v1/analyze/message", response_model=Decision)
def analyze_message(message: Message):
    decision = analyze(message)
    event_id = f"api:{message.chat_id or 'unknown'}:{message.message_id}"
    store.put(event_id, message.chat_id or "unknown", message.message_id, message.text, decision.model_dump_json())
    return decision

@app.post("/api/v1/ingest/telegram")
def ingest_telegram(payload: TelegramUpdate):
    event = normalize_update(payload.update)
    if event is None:
        return {"accepted": False, "reason": "unsupported_or_empty_update"}
    if store.seen(event.event_id):
        return {"accepted": True, "duplicate": True, "event_id": event.event_id}
    message = Message(message_id=event.message_id, chat_id=event.chat_id, text=event.text)
    decision = analyze(message)
    store.put(event.event_id, event.chat_id, event.message_id, event.text, decision.model_dump_json())
    return {"accepted": True, "duplicate": False, "event_id": event.event_id, "decision": decision.model_dump()}
