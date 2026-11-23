from __future__ import annotations

from dataclasses import dataclass
from app import Message, baseline

@dataclass(frozen=True)
class Case:
    text: str
    intent: str
    min_score: int

CASES = [
    Case("Сколько стоит заказать сегодня?", "buying", 90),
    Case("Хочу купить, сколько стоит?", "buying", 78),
    Case("Можно оплатить сейчас?", "buying", 78),
    Case("Мне нужна услуга на сегодня", "buying", 90),
    Case("Есть свободное время завтра?", "information", 28),
    Case("Как вы работаете?", "information", 28),
    Case("Где вы находитесь?", "information", 28),
    Case("Какие условия?", "information", 28),
]

def evaluate() -> dict:
    correct = 0
    score_ok = 0
    for i, case in enumerate(CASES):
        d = baseline(Message(message_id=f"eval-{i}", text=case.text))
        correct += d.intent == case.intent
        score_ok += d.lead_score >= case.min_score
    n = len(CASES)
    return {
        "cases": n,
        "intent_accuracy": correct / n,
        "score_threshold_pass_rate": score_ok / n,
        "baseline": "deterministic",
    }

if __name__ == "__main__":
    print(evaluate())
