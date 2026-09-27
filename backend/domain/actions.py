def build_profit_actions(items, low_stock_threshold=5, low_margin_percent=15.0):
    """Turn inventory state into concrete, reviewable business actions."""
    actions = []
    for item in items:
        qty = float(item.get("quantity") or 0)
        cost = int(item.get("unit_price_minor") or 0)
        sale = item.get("sale_price_minor")
        name = item.get("name", "item")

        if qty <= low_stock_threshold:
            actions.append({
                "type": "LOW_STOCK",
                "priority": "high" if qty <= 1 else "medium",
                "item": name,
                "message": f"Остаток {qty:g}. Проверь закупку товара.",
            })

        if sale is None or int(sale) <= 0:
            actions.append({
                "type": "MISSING_SALE_PRICE",
                "priority": "high",
                "item": name,
                "message": "Не задана цена продажи — прибыль по товару не рассчитывается.",
            })
            continue

        sale = int(sale)
        margin = ((sale - cost) / sale * 100.0) if sale > 0 else 0.0
        if margin < 0:
            actions.append({
                "type": "NEGATIVE_MARGIN",
                "priority": "critical",
                "item": name,
                "margin_percent": round(margin, 2),
                "message": "Цена продажи ниже себестоимости.",
            })
        elif margin < low_margin_percent:
            actions.append({
                "type": "LOW_MARGIN",
                "priority": "high",
                "item": name,
                "margin_percent": round(margin, 2),
                "message": f"Маржа {margin:.1f}%. Проверь цену продажи.",
            })

    priority = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    actions.sort(key=lambda x: (priority.get(x.get("priority"), 9), x.get("item", "")))
    return actions
