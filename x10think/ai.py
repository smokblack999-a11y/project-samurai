from __future__ import annotations

import json
import os
from typing import Any

SYSTEM = """You are X10THINK Sentinel. Analyze infrastructure telemetry only.
Return strict JSON with keys: summary, severity, findings, next_steps.
Severity must be one of: low, medium, high, critical.
Never invent measurements. Never propose destructive commands.
Recommendations must be reversible and safe.
"""


def _parse_json(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {"summary": text}
    except json.JSONDecodeError:
        return {"summary": text, "parse_warning": "model_output_was_not_json"}


def _together_analyze(payload: dict) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["TOGETHER_API_KEY"],
        base_url="https://api.together.ai/v1",
    )
    response = client.chat.completions.create(
        model=os.getenv("X10_TOGETHER_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(payload, separators=(",", ":"))},
        ],
        response_format={"type": "json_object"},
        max_tokens=700,
        reasoning_effort=os.getenv("X10_TOGETHER_REASONING", "low"),
    )
    text = response.choices[0].message.content or "{}"
    return {"enabled": True, "provider": "together", "model": response.model, "analysis": _parse_json(text)}


def _openai_analyze(payload: dict) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model=os.getenv("X10_OPENAI_MODEL", "gpt-5-mini"),
        instructions=SYSTEM,
        input=json.dumps(payload, separators=(",", ":")),
    )
    return {
        "enabled": True,
        "provider": "openai",
        "model": response.model,
        "analysis": _parse_json(response.output_text),
    }


def analyze(payload: dict) -> dict[str, Any]:
    """Run guarded diagnostics using Together first, then OpenAI as fallback."""
    provider = os.getenv("X10_AI_PROVIDER", "auto").lower()
    providers: list[str]
    if provider == "together":
        providers = ["together"]
    elif provider == "openai":
        providers = ["openai"]
    else:
        providers = ["together", "openai"]

    configured = {
        "together": bool(os.getenv("TOGETHER_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
    }
    attempted = [name for name in providers if configured[name]]
    if not attempted:
        return {"enabled": False, "reason": "No AI provider API key is configured."}

    errors: list[str] = []
    for name in attempted:
        try:
            return _together_analyze(payload) if name == "together" else _openai_analyze(payload)
        except Exception as exc:
            errors.append(f"{name}:{type(exc).__name__}")

    return {"enabled": False, "error": ";".join(errors)}
