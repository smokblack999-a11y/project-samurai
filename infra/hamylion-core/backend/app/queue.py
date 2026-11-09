import json,redis.asyncio as redis
from .config import settings
client=redis.from_url(settings.REDIS_URL,decode_responses=True)
STREAM='hamylion.events'; GROUP='hamylion-workers'
async def enqueue(event:dict,delay_seconds:float=0):
    if delay_seconds>0: event={**event,'not_before':delay_seconds}
    return await client.xadd(STREAM,{'event':json.dumps(event)},maxlen=100000,approximate=True)
async def ensure_group():
    try: await client.xgroup_create(STREAM,GROUP,id='0',mkstream=True)
    except Exception: pass
async def reclaim_idle(min_idle_ms=30000): return await client.xautoclaim(STREAM,GROUP,'recovery',min_idle_ms,'0-0',count=50)
