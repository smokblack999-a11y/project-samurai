import os

os.environ["DATABASE_URL"] = "sqlite:///./test_stockscan.db"
os.environ["STOCKSCAN_API_TOKEN"] = "test-token"

from core.schemas import ConfirmItem
from db.database import init_db
from db.repositories import add_inventory, dashboard, set_sale_price


def test_purchase_to_profit_dashboard(tmp_path, monkeypatch):
    db = tmp_path / "stockscan.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    from core.config import get_settings
    get_settings.cache_clear()
    init_db()

    result = add_inventory([
        ConfirmItem(name=" Milk  ", quantity=10, unit_price_minor=500, currency="kzt")
    ], "profit-test-123")
    assert result["confirmed"] == 1

    set_sale_price(result["ids"][0], 800)
    data = dashboard()
    assert data["items"][0]["name"] == "Milk"
    assert data["items"][0]["margin_percent"] == 37.5
    assert data["items"][0]["profit_minor"] == 3000
    assert data["total_stock_cost_minor"] == 5000
    assert data["total_expected_profit_minor"] == 3000
