from app.decision import classify
from app.evaluation import run_evaluation

CASES = [
    ("Сколько стоит заказать услугу?", "buying"),
    ("Можно сегодня?", "information"),
    ("Хочу купить, сколько стоит?", "buying"),
    ("Просто интересуюсь", "information"),
    ("Есть свободное время завтра?", "information"),
    ("Нужно срочно заказать", "buying"),
    ("Скиньте описание услуги", "information"),
    ("Как оплатить?", "buying"),
]


def test_baseline_dataset_accuracy():
    results = [classify(text)["intent"] == expected for text, expected in CASES]
    accuracy = sum(results) / len(results)
    assert accuracy >= 0.875


def test_execution_evaluation_gate():
    result = run_evaluation()
    assert result["total"] >= 5
    assert result["pass_rate"] == 1.0
