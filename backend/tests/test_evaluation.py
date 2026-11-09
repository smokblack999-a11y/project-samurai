CASES = [
    {"text": "Сколько стоит доставка сегодня?", "expected_intent": "buying", "min_score": 70},
    {"text": "Просто хотел узнать, есть ли у вас такая услуга", "expected_intent": "question", "min_score": 20},
    {"text": "Мне нужна помощь с уже оплаченной услугой", "expected_intent": "support", "min_score": 20},
    {"text": "Куплю, если сможете сделать сегодня", "expected_intent": "buying", "min_score": 75},
]

def test_dataset_is_nonempty_and_bounded():
    assert len(CASES) >= 4
    assert all(0 <= case["min_score"] <= 100 for case in CASES)
