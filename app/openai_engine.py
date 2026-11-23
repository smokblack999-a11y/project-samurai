from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from .decision import classify
from .schemas import LeadDecision

SYSTEM_PROMPT = """You classify inbound Telegram business messages into a strict lead decision.
Return JSON only with keys: intent, lead_score, urgency, recommended_action, needs, reason.
intent is buying or information. lead_score is integer 0..100. urgency is high or low.
recommended_action is human_followup or auto_reply. needs is an array of short strings.
Do not invent facts that are not present in the message.
"""


def analyze(text: str) -> dict[str, Any]:
    if not os.getenv("OPENAI_API_KEY"):
        return classify(text)

    try:
        client = OpenAI(timeout=float(os.getenv("OPENAI_TIMEOUT", "12")), max_retries=2)
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            input=text,
        )
        raw = response.output_text.strip()
        data = json.loads(raw)
        decision = LeadDecision.model_validate(data)
        return decision.model_dump()
    except (json.JSONDecodeError, ValidationError):
        return classify(text)
    except Exception:
        # Network/provider failures never block the deterministic path.
        return classify(text)
