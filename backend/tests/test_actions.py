from domain.actions import build_profit_actions


def test_profit_actions_prioritize_negative_margin_and_missing_price():
    items = [
        {"name": "Milk", "quantity": 1, "unit_price_minor": 1000, "sale_price_minor": 900},
        {"name": "Bread", "quantity": 20, "unit_price_minor": 500, "sale_price_minor": None},
        {"name": "Water", "quantity": 3, "unit_price_minor": 500, "sale_price_minor": 700},
    ]
    actions = build_profit_actions(items)
    assert actions[0]["type"] == "NEGATIVE_MARGIN"
    assert any(a["type"] == "MISSING_SALE_PRICE" for a in actions)
    assert any(a["type"] == "LOW_STOCK" and a["item"] == "Water" for a in actions)


def test_profit_actions_do_not_flag_healthy_item():
    items = [{"name": "Rice", "quantity": 50, "unit_price_minor": 1000, "sale_price_minor": 1500}]
    assert build_profit_actions(items) == []
