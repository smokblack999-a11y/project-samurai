from fastapi import APIRouter, Header, HTTPException, Query
from core.config import get_settings
from core.schemas import ConfirmRequest
from db.repositories import add_inventory, list_inventory, list_ledger

router = APIRouter()


def auth(token):
    if token != get_settings().stockscan_api_token:
        raise HTTPException(401, "invalid API token")


@router.post("/inventory/confirm")
def confirm(
    req: ConfirmRequest,
    x_stockscan_token: str | None = Header(None),
    x_idempotency_key: str | None = Header(None),
):
    auth(x_stockscan_token)
    if x_idempotency_key and (len(x_idempotency_key) < 8 or len(x_idempotency_key) > 128):
        raise HTTPException(400, "invalid idempotency key")
    try:
        return add_inventory(req.items, x_idempotency_key)
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.get("/inventory")
def inventory(x_stockscan_token: str | None = Header(None)):
    auth(x_stockscan_token)
    return {"items": list_inventory()}


@router.get("/inventory/ledger")
def ledger(
    x_stockscan_token: str | None = Header(None),
    limit: int = Query(200, ge=1, le=1000),
):
    auth(x_stockscan_token)
    return {"entries": list_ledger(limit)}
