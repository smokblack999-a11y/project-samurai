def test_catalog_matching_prefers_exact_sku_and_flags_new_product(tmp_path, monkeypatch):
    db_file = tmp_path / "catalog.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    from core.config import get_settings
    get_settings.cache_clear()
    from db.database import init_db
    from db.repositories import add_inventory, match_inventory_items
    from core.schemas import ConfirmItem, MatchItem

    init_db()
    add_inventory([
        ConfirmItem(name="Coca Cola 0.5L", sku="12345", quantity=10, unit_price_minor=300, currency="KZT"),
        ConfirmItem(name="Fanta Orange 0.5L", sku="67890", quantity=5, unit_price_minor=300, currency="KZT"),
    ], "seed-12345678")

    exact = match_inventory_items([MatchItem(name="Coca-Cola 0,5 л", sku="12345", currency="KZT")])[0]
    assert exact["decision"] == "auto_match"
    assert exact["candidates"][0]["reason"] == "exact_sku"
    assert exact["candidates"][0]["score"] == 1.0

    fuzzy = match_inventory_items([MatchItem(name="Fanta Orange 0.5 L", currency="KZT")])[0]
    assert fuzzy["decision"] in {"auto_match", "review_match"}
    assert fuzzy["candidates"][0]["name"] == "Fanta Orange 0.5L"

    new = match_inventory_items([MatchItem(name="Pepsi 0.5L", currency="KZT")])[0]
    assert new["decision"] == "new_product"
