from __future__ import annotations

from .decision import classify

CASES = [
    ("Сколько стоит заказать услугу?", "buying", 78, "human_followup"),
    ("Мне нужно купить это сегодня", "buying", 90, "human_followup"),
    ("Есть ли свободное место сегодня?", "information", 33, "auto_reply"),
    ("Как вы работаете?", "information", 28, "auto_reply"),
    ("Цена и можно ли заказать сейчас?", "buying", 90, "human_followup"),
]


def run_evaluation() -> dict:
    passed = 0
    results = []

    for text, expected_intent, minimum_score, expected_action in CASES:
        actual = classify(text)
        ok = (
            actual["intent"] == expected_intent
            and actual["lead_score"] >= minimum_score
            and actual["recommended_action"] == expected_action
        )
        passed += int(ok)
        results.append({
            "text": text,
            "passed": ok,
            "actual": actual,
        })

    return {
        "passed": passed,
        "total": len(CASES),
        "pass_rate": passed / len(CASES),
        "results": results,
    }
