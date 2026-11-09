from __future__ import annotations

import re

BUYING_TERMS = (
    "купить", "цена", "стоимость", "заказать", "сколько стоит", "оплатить",
    "buy", "price", "cost", "order", "purchase",
)
URGENT_TERMS = (
    "сегодня", "срочно", "сейчас", "как можно скорее", "today", "urgent", "now",
)
PRICE_TERMS = ("цена", "стоимость", "сколько стоит", "price", "cost")
AVAILABILITY_TERMS = ("есть", "свободно", "доступно", "можно сегодня", "available")


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    value = text.casefold()
    return any(term in value for term in terms)


def classify(text: str) -> dict:
    normalized = re.sub(r"\s+", " ", text).strip()
    buying = _contains(normalized, BUYING_TERMS)
    urgent = _contains(normalized, URGENT_TERMS)
    price = _contains(normalized, PRICE_TERMS)
    availability = _contains(normalized, AVAILABILITY_TERMS)

    score = 78 if buying else 28
    if urgent:
        score += 12
    if availability:
        score += 5
    score = min(score, 100)

    return {
        "intent": "buying" if buying else "information",
        "lead_score": score,
        "urgency": "high" if urgent or buying else "low",
        "recommended_action": "human_followup" if buying else "auto_reply",
        "needs": [x for x, enabled in (("price", price), ("availability", availability)) if enabled],
        "reason": "Explicit purchase intent detected by deterministic baseline" if buying else "No explicit purchase intent detected",
    }
