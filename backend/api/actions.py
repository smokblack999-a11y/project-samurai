from fastapi import APIRouter, Header, HTTPException, Query
from core.config import get_settings
from db.repositories import list_inventory
from domain.actions import build_profit_actions

router = APIRouter()


def auth(token):
    if token != get_settings().stockscan_api_token:
        raise HTTPException(401, "invalid API token")


@router.get("/actions")
def actions(
    x_stockscan_token: str | None = Header(None),
    low_stock_threshold: int = Query(5, ge=0, le=100000),
    low_margin_percent: float = Query(15.0, ge=0, le=100),
):
    auth(x_stockscan_token)
    items = list_inventory()
    result = build_profit_actions(items, low_stock_threshold, low_margin_percent)
    return {"count": len(result), "actions": result}
