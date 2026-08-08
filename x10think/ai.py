from __future__ import annotations

import json
import os
from typing import Any


SYSTEM_PROMPT = """You are X10THINK Sentinel. Analyze infrastructure telemetry conservatively. Return JSON with diagnosis, severity, confidence, and recommended_safe_actions. Never invent facts and never recommend destructive actions without explicit approval."""


def analyze(state: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return {"available": False, "reason": "OPENAI_API_KEY is not set"}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.responses.create(
            model=os.getenv("X10_OPENAI_MODEL", "gpt-5-mini"),
            instructions=SYSTEM_PROMPT,
            input=json.dumps(state, ensure_ascii=False),
        )
        return {"available": True, "analysis": response.output_text}
    except Exception as exc:
        return {"available": False, "reason": f"AI request failed: {type(exc).__name__}"}
