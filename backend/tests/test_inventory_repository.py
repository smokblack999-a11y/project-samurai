from pathlib import Path


def test_inventory_confirmation_is_idempotent(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    from core.config import get_settings
    get_settings.cache_clear()
    from db.database import init_db
    from db.repositories import add_inventory, list_inventory, list_ledger
    from core.schemas import ConfirmItem

    init_db()
    item = ConfirmItem(name="Coffee", quantity=2, unit_price_minor=1000, currency="KZT")

    first = add_inventory([item], "receipt-12345678")
    second = add_inventory([item], "receipt-12345678")

    assert first == second
    assert list_inventory()[0]["quantity"] == 2
    assert len(list_ledger()) == 1

    third = add_inventory([ConfirmItem(name="Coffee", quantity=3, unit_price_minor=1100, currency="KZT")], "receipt-87654321")
    assert third["confirmed"] == 1
    assert list_inventory()[0]["quantity"] == 5
    assert list_inventory()[0]["unit_price_minor"] == 1100
