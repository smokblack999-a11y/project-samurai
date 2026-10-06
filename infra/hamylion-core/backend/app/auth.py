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
