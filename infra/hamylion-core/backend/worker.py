import asyncio,json,random
from datetime import datetime,timedelta
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Event,Outbox
from app.queue import client,STREAM,GROUP,ensure_group,reclaim_idle,enqueue
from app.config import settings
from app.websocket import manager

def event_message(e,**extra):
    data={'id':e.id,'project_id':e.project_id,'type':e.event_type,'payload':e.payload}
    data.update(extra)
    return data

async def process(mid,fields):
    event=json.loads(fields['event'])
    eid=event['id']
    async with SessionLocal() as s:
        e=await s.get(Event,eid)
        if not e or e.status=='delivered':
            await client.xack(STREAM,GROUP,mid)
            return
        if e.status=='retrying' and e.retry_at and e.retry_at>datetime.utcnow():
            await client.xack(STREAM,GROUP,mid)
            return
        if e.attempts>=settings.MAX_RETRIES:
            e.status='dead_letter'
            e.last_error=e.last_error or 'max_retries_exceeded'
            e.retry_at=None
            await s.commit()
            await client.xack(STREAM,GROUP,mid)
            return
        e.status='delivering'
        e.attempts+=1
        e.delivery_started_at=datetime.utcnow()
        e.retry_at=None
        e.last_error=None
        await s.commit()
    try:
        await manager.broadcast(event['project_id'],{
            'event_id':eid,'type':event['type'],
            'payload':event['payload'],'status':'delivering'
        })
        await client.xack(STREAM,GROUP,mid)
    except Exception as exc:
        async with SessionLocal() as s:
            e=await s.get(Event,eid)
            if e:
                if e.attempts>=settings.MAX_RETRIES:
                    e.status='dead_letter'
                    e.last_error=str(exc)[:2000]
                    e.retry_at=None
                else:
                    delay=min(
                        settings.RETRY_MAX_SECONDS,
                        settings.RETRY_BASE_SECONDS*(2**max(e.attempts-1,0))
                    )*random.uniform(0.8,1.2)
                    e.status='retrying'
                    e.last_error=str(exc)[:2000]
                    e.retry_at=datetime.utcnow()+timedelta(seconds=delay)
                await s.commit()
        raise

async def recover_stale_deliveries():
    cutoff=datetime.utcnow()-timedelta(seconds=settings.DELIVERY_TIMEOUT_SECONDS)
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Event).where(
                Event.status=='delivering',
                Event.delivery_started_at.is_not(None),
                Event.delivery_started_at<cutoff,
            ).limit(100).with_for_update(skip_locked=True)
        )).scalars().all()
        for e in rows:
            if e.attempts>=settings.MAX_RETRIES:
                e.status='dead_letter'
                e.last_error='delivery_ack_timeout'
                e.retry_at=None
            else:
                delay=min(
                    settings.RETRY_MAX_SECONDS,
                    settings.RETRY_BASE_SECONDS*(2**max(e.attempts-1,0))
                )*random.uniform(0.8,1.2)
                e.status='retrying'
                e.last_error='delivery_ack_timeout'
                e.retry_at=datetime.utcnow()+timedelta(seconds=delay)
        await s.commit()

async def enqueue_due_retries():
    now=datetime.utcnow()
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Event)
            .where(
                Event.status=='retrying',
                Event.retry_at.is_not(None),
                Event.retry_at<=now,
            )
            .order_by(Event.retry_at)
            .limit(100)
            .with_for_update(skip_locked=True)
        )).scalars().all()
        for e in rows:
            e.status='queued'
            e.retry_at=None
            s.add(Outbox(
                id='obx_retry_'+e.id+'_'+str(int(now.timestamp()*1000000)),
                event_id=e.id,
                payload=event_message(e,recovery=True),
            ))
        await s.commit()

async def dispatch_outbox(batch_size=100):
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Outbox)
            .where(Outbox.published_at.is_(None))
            .order_by(Outbox.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )).scalars().all()
        for row in rows:
            try:
                await enqueue(row.payload)
                row.published_at=datetime.utcnow()
                row.last_error=None
            except Exception as exc:
                row.attempts+=1
                row.last_error=str(exc)[:2000]
        await s.commit()

async def handle_messages(messages):
    for _,entries in messages:
        for mid,fields in entries:
            try:
                await process(mid,fields)
            except Exception:
                # The DB state records retry/dead-letter decisions.
                # A failed Redis message remains pending for reclaim.
                pass

async def main():
    await ensure_group()
    while True:
        try:
            claimed=await reclaim_idle()
            if len(claimed)>1 and claimed[1]:
                await handle_messages([(STREAM,claimed[1])])
            await recover_stale_deliveries()
            await enqueue_due_retries()
            await dispatch_outbox()
            messages=await client.xreadgroup(
                GROUP,'worker-1',{STREAM:'>'},count=20,block=5000
            )
            if messages:
                await handle_messages(messages)
        except Exception:
            await asyncio.sleep(2)

if __name__=='__main__':
    asyncio.run(main())
