from __future__ import annotations

import json
import os
from typing import Any

SYSTEM = """You are X10THINK Sentinel. Analyze infrastructure telemetry only.
Never invent measurements. Never propose destructive commands. Recommendations must be reversible and safe.
Return only the requested JSON object.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "findings": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "severity", "findings", "next_steps"],
    "additionalProperties": False,
}


def _provider() -> str:
    value = os.getenv("X10_AI_PROVIDER", "auto").strip().lower()
    if value in {"openai", "together"}:
        return value
    if os.getenv("TOGETHER_API_KEY"):
        return "together"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "none"


def _parse_json(content: str) -> dict[str, Any]:
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("AI response is not a JSON object")
    for key in ("summary", "severity", "findings", "next_steps"):
        if key not in data:
            raise ValueError(f"AI response missing key: {key}")
    return data


def _chat(provider: str, payload: dict) -> dict[str, Any]:
    from openai import OpenAI

    if provider == "together":
        client = OpenAI(
            api_key=os.environ["TOGETHER_API_KEY"],
            base_url="https://api.together.ai/v1",
            timeout=float(os.getenv("X10_AI_TIMEOUT", "20")),
        )
        model = os.getenv("X10_TOGETHER_MODEL", "openai/gpt-oss-20b")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "x10think_analysis", "schema": SCHEMA},
            },
            max_tokens=int(os.getenv("X10_AI_MAX_TOKENS", "700")),
            temperature=0,
        )
    else:
        client = OpenAI(timeout=float(os.getenv("X10_AI_TIMEOUT", "20")))
        model = os.getenv("X10_OPENAI_MODEL", "gpt-5-mini")
        response = client.responses.create(
            model=model,
            instructions=SYSTEM,
            input=json.dumps(payload, sort_keys=True),
        )
        return _parse_json(response.output_text)

    content = response.choices[0].message.content or ""
    return _parse_json(content)


def analyze(payload: dict) -> dict:
    provider = _provider()
    if provider == "none":
        return {"enabled": False, "reason": "No AI provider is configured."}
    try:
        result = _chat(provider, payload)
        return {
            "enabled": True,
            "provider": provider,
            "model": os.getenv(
                "X10_TOGETHER_MODEL" if provider == "together" else "X10_OPENAI_MODEL",
                "openai/gpt-oss-20b" if provider == "together" else "gpt-5-mini",
            ),
            "analysis": result,
        }
    except Exception as exc:
        return {"enabled": False, "provider": provider, "error": type(exc).__name__}
