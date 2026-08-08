from __future__ import annotations

import os

SYSTEM = """You are X10THINK Sentinel. Analyze infrastructure telemetry only. Return concise JSON with keys: summary, severity, findings, next_steps. Never invent measurements. Do not propose destructive commands. Recommendations must be reversible and safe."""


def analyze(payload: dict) -> dict:
    if not os.getenv("OPENAI_API_KEY"):
        return {"enabled": False, "reason": "OPENAI_API_KEY is not configured."}
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("X10_OPENAI_MODEL", "gpt-5-mini"),
            instructions=SYSTEM,
            input=str(payload),
        )
        return {"enabled": True, "analysis": response.output_text}
    except Exception as exc:
        return {"enabled": False, "error": type(exc).__name__}
