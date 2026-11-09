import json
import os
from openai import OpenAI
from .models import AnalyzeMessageRequest, LeadDecision

SYSTEM = """You are a conservative Telegram business lead classifier. Return ONLY valid JSON matching the requested schema. Never invent contact details. Score purchase intent, urgency and required human action. If uncertain, lower confidence through the score rather than fabricating facts."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {"type": "string", "enum": ["buying", "question", "support", "spam", "other"]},
        "lead_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "language": {"type": "string"},
        "needs": {"type": "array", "items": {"type": "string"}},
        "recommended_action": {"type": "string", "enum": ["human_followup", "reply", "ignore", "escalate"]},
        "reason": {"type": "string"}
    },
    "required": ["intent", "lead_score", "urgency", "language", "needs", "recommended_action", "reason"]
}

def analyze(req: AnalyzeMessageRequest) -> LeadDecision:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    client = OpenAI(api_key=key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        instructions=SYSTEM,
        input=f"message_id={req.message_id}\ntext={req.text}\nlanguage_hint={req.language_hint or ''}",
        text={"format": {"type": "json_schema", "name": "lead_decision", "strict": True, "schema": SCHEMA}},
    )
    data = json.loads(response.output_text)
    return LeadDecision(message_id=req.message_id, **data)
