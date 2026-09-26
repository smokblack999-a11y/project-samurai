import json
import redis.asyncio as redis
from .config import settings

client=redis.from_url(settings.REDIS_URL,decode_responses=True)
STREAM='hamylion.events'
DLQ_STREAM='hamylion.dlq'
GROUP='hamylion-workers'

async def enqueue(event:dict):
    return await client.xadd(STREAM,{'event':json.dumps(event)},maxlen=100000,approximate=True)

async def enqueue_dlq(event:dict, reason:str):
    return await client.xadd(DLQ_STREAM,{'event':json.dumps(event),'reason':reason},maxlen=100000,approximate=True)

async def ensure_group():
    try:
        await client.xgroup_create(STREAM,GROUP,id='0',mkstream=True)
    except Exception:
        pass

async def reclaim_idle(min_idle_ms=None):
    return await client.xautoclaim(
        STREAM,GROUP,settings.WORKER_NAME,
        min_idle_ms or settings.RECOVERY_IDLE_MS,
        '0-0',count=50
    )
