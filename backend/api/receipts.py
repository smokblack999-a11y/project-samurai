from fastapi import APIRouter,UploadFile,File,Header,HTTPException
from fastapi.concurrency import run_in_threadpool
from core.config import get_settings
from core.receipt_extractor import extract
from core.validation import validate_receipt
router=APIRouter()
def auth(token):
    if token!=get_settings().stockscan_api_token: raise HTTPException(401,"invalid API token")
@router.post("/receipts/extract")
async def extract_receipt(file:UploadFile=File(...),x_stockscan_token:str|None=Header(None)):
    auth(x_stockscan_token)
    if not file.content_type or not file.content_type.startswith("image/"): raise HTTPException(415,"image required")
    raw=await file.read()
    if len(raw)>get_settings().max_image_mb*1024*1024: raise HTTPException(413,"image too large")
    try: receipt=await run_in_threadpool(extract,raw)
    except RuntimeError as exc: raise HTTPException(503,str(exc))
    return {"receipt":receipt.model_dump(),"validation":validate_receipt(receipt).model_dump()}
