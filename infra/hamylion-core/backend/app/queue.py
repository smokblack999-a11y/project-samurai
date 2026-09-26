import json
import redis.asyncio as redis
from .config import settings

client=redis.from_url(settings.REDIS_URL,decode_responses=True)
STREAM='hamylion.events'
DLQ_STREAM='hamylion.dlq'
RETRY_ZSET='hamylion.retry'
GROUP='hamylion-workers'

async def enqueue(event:dict):
    # PostgreSQL remains the durable source of truth. Do not MAXLEN-trim the
    # transport stream: Redis can otherwise delete payloads that are still
    # pending in the consumer group's PEL.
    return await client.xadd(STREAM,{'event':json.dumps(event)})

async def enqueue_dlq(event:dict, reason:str):
    return await client.xadd(DLQ_STREAM,{'event':json.dumps(event),'reason':reason})

async def schedule_retry(event:dict, due_at:float):
    await client.zadd(RETRY_ZSET,{json.dumps(event,sort_keys=True):due_at})

async def drain_due_retries(limit:int=50):
    import time
    members=await client.zrangebyscore(RETRY_ZSET,0,time.time(),start=0,num=limit)
    events=[]
    for member in members:
        if not await client.zrem(RETRY_ZSET,member):
            continue
        event = json.loads(member)
        try:
            await enqueue(event)
            events.append(event)
        except Exception:
            await client.zadd(RETRY_ZSET,{member: time.time() + 1})
    return events

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

async def ack_and_cleanup(message_id: str):
    await client.xack(STREAM,GROUP,message_id)
    await client.xdel(STREAM,message_id)
