import hashlib
from fastapi import Header,HTTPException
from sqlalchemy import select
from .config import settings
from .db import SessionLocal
from .models import ApiKey,Project

def _hash(value:str)->str:
    return hashlib.sha256(value.encode()).hexdigest()

async def validate_api_key(x_api_key:str|None=Header(default=None)):
    if not x_api_key: raise HTTPException(401,'Missing API key')
    async with SessionLocal() as s:
        row=(await s.execute(select(ApiKey,Project).join(Project,Project.id==ApiKey.project_id).where(ApiKey.key_hash==_hash(x_api_key),ApiKey.active==True))).first()
    if row: return row[0].project_id
    if settings.API_KEY and x_api_key==settings.API_KEY: return 'default-project'
    raise HTTPException(401,'Invalid API key')

import base64,hmac,json,secrets,time

def _token_secret():
    secret=getattr(settings,'WS_TOKEN_SECRET','') or settings.API_KEY
    if not secret:
        raise HTTPException(503,'WebSocket token signing is not configured')
    return secret.encode()

def issue_ws_token(project_id:str,ttl_seconds:int=60)->str:
    payload={'project_id':project_id,'exp':int(time.time())+ttl_seconds,'nonce':secrets.token_urlsafe(12)}
    raw=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':')).encode()).decode().rstrip('=')
    sig=hmac.new(_token_secret(),raw.encode(),hashlib.sha256).hexdigest()
    return raw+'.'+sig

def verify_ws_token(token:str,project_id:str)->bool:
    try:
        raw,sig=token.rsplit('.',1)
        expected=hmac.new(_token_secret(),raw.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig,expected): return False
        payload=json.loads(base64.urlsafe_b64decode(raw+'='*((4-len(raw)%4)%4)))
        return payload.get('project_id')==project_id and int(payload.get('exp',0))>=int(time.time())
    except Exception:
        return False
