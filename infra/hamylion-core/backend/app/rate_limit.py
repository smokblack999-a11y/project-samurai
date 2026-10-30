from fastapi import Depends,HTTPException
from .auth import validate_api_key
from .queue import client
from .config import settings

async def enforce_project_rate_limit(project_id:str=Depends(validate_api_key)):
    window=60
    key=f"hamylion:rate:{project_id}"
    async with client.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key,window,nx=True)
        result=await pipe.execute()
    count=int(result[0])
    if count>settings.RATE_LIMIT_PER_MINUTE:
        ttl=await client.ttl(key)
        raise HTTPException(status_code=429,detail="rate_limit_exceeded",headers={"Retry-After":str(max(int(ttl),1))})
    return project_id
