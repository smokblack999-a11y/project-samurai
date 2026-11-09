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
    Case("Сколько стоит и можно ли сегодня?", "buying", 90, "human_followup"),
    Case("Хочу заказать услугу на завтра", "buying", 78, "human_followup"),
    Case("Можно оплатить картой?", "buying", 78, "human_followup"),
    Case("Мне нужна цена", "buying", 78, "human_followup"),
    Case("Хочу купить сейчас", "buying", 90, "human_followup"),
    Case("Сколько стоит доставка?", "buying", 78, "human_followup"),
    Case("Есть возможность оформить заказ?", "buying", 78, "human_followup"),
    Case("Готов оплатить сегодня", "buying", 90, "human_followup"),
    Case("Можно забронировать на завтра?", "buying", 78, "human_followup"),
    Case("Мне нужна стоимость услуги", "buying", 78, "human_followup"),
    Case("Как вы работаете?", "information", 28, "auto_reply"),
    Case("Где вы находитесь?", "information", 28, "auto_reply"),
    Case("Какие у вас услуги?", "information", 28, "auto_reply"),
    Case("Какие у вас условия?", "information", 28, "auto_reply"),
    Case("Расскажите подробнее", "information", 28, "auto_reply"),
    Case("Есть ли такая услуга?", "information", 28, "auto_reply"),
    Case("Как с вами связаться?", "information", 28, "auto_reply"),
    Case("В какие часы вы работаете?", "information", 28, "auto_reply"),
    Case("Есть ли свободное время сегодня?", "information", 28, "auto_reply"),
    Case("Какой адрес?", "information", 28, "auto_reply"),
]

def run() -> dict:
    correct_intent = correct_action = score_ok = 0
    rows = []
    for i, case in enumerate(CASES, 1):
        d = baseline(Message(message_id=f"eval-{i}", text=case.text))
        intent_ok = d.intent == case.expected_intent
        action_ok = d.recommended_action == case.expected_action
        score_ok_i = d.lead_score >= case.min_score
        correct_intent += intent_ok
        correct_action += action_ok
        score_ok += score_ok_i
        rows.append({"text": case.text, "intent_ok": intent_ok, "action_ok": action_ok, "score_ok": score_ok_i, "score": d.lead_score})
    n = len(CASES)
    return {
        "cases": n,
        "intent_accuracy": correct_intent / n,
        "action_accuracy": correct_action / n,
        "score_threshold_rate": score_ok / n,
        "rows": rows,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
