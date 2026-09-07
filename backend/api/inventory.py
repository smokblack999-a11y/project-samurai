from fastapi import APIRouter,Header,HTTPException
from core.config import get_settings
from core.schemas import ConfirmRequest
from db.repositories import add_inventory,list_inventory
router=APIRouter()
def auth(token):
    if token!=get_settings().stockscan_api_token: raise HTTPException(401,"invalid API token")
@router.post("/inventory/confirm")
def confirm(req:ConfirmRequest,x_stockscan_token:str|None=Header(None)):
    auth(x_stockscan_token); ids=add_inventory(req.items); return {"confirmed":len(ids),"ids":ids}
@router.get("/inventory")
def inventory(x_stockscan_token:str|None=Header(None)):
    auth(x_stockscan_token); return {"items":list_inventory()}
