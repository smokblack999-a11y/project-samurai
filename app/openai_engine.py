from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .decision import classify

SYSTEM_PROMPT = """You classify inbound Telegram business messages into a strict lead decision.
Return JSON only with keys: intent, lead_score, urgency, recommended_action, needs, reason.
intent is buying or information. lead_score is integer 0..100. urgency is high or low.
recommended_action is human_followup or auto_reply. needs is an array of strings.
Do not invent facts that are not present in the message."""


def analyze(text: str) -> dict[str, Any]:
    if os.getenv("OPENAI_API_KEY") is None:
        return classify(text)

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=text,
    )
    raw = response.output_text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return classify(text)

    # Fail closed: malformed model output never becomes a production decision.
    required = {"intent", "lead_score", "urgency", "recommended_action", "needs", "reason"}
    if not required.issubset(data):
        return classify(text)
    if data["intent"] not in {"buying", "information"}:
        return classify(text)
    if data["urgency"] not in {"high", "low"}:
        return classify(text)
    if data["recommended_action"] not in {"human_followup", "auto_reply"}:
        return classify(text)
    if not isinstance(data["lead_score"], int) or not 0 <= data["lead_score"] <= 100:
        return classify(text)
    if not isinstance(data["needs"], list):
        return classify(text)
    return data
