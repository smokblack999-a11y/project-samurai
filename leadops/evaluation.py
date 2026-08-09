from __future__ import annotations

from dataclasses import dataclass
from app import Message, baseline

@dataclass(frozen=True)
class Case:
    text: str
    expected_intent: str
    min_score: int
    expected_action: str

CASES = [
    Case("Сколько стоит заказать сегодня?", "buying", 90, "human_followup"),
    Case("Хочу купить, есть ли в наличии?", "buying", 78, "human_followup"),
    Case("Можно оплатить сейчас?", "buying", 78, "human_followup"),
    Case("Нужна цена на услугу", "buying", 78, "human_followup"),
    Case("Как вы работаете?", "information", 28, "auto_reply"),
    Case("Расскажите подробнее", "information", 28, "auto_reply"),
    Case("Есть ли такая услуга?", "information", 28, "auto_reply"),
    Case("Какие у вас условия?", "information", 28, "auto_reply"),
]

def run() -> dict:
    correct_intent = 0
    correct_action = 0
    score_ok = 0
    rows = []
    for i, case in enumerate(CASES, 1):
        decision = baseline(Message(message_id=f"eval-{i}", text=case.text))
        intent_ok = decision.intent == case.expected_intent
        action_ok = decision.recommended_action == case.expected_action
        score_ok_i = decision.lead_score >= case.min_score
        correct_intent += intent_ok
        correct_action += action_ok
        score_ok += score_ok_i
        rows.append({"text": case.text, "intent_ok": intent_ok, "action_ok": action_ok, "score_ok": score_ok_i})
    n = len(CASES)
    return {"cases": n, "intent_accuracy": correct_intent / n, "action_accuracy": correct_action / n, "score_threshold_rate": score_ok / n, "rows": rows}

if __name__ == "__main__":
    print(run())
