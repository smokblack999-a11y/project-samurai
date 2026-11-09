from app.decision import classify

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
