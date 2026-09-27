import asyncio
import json
import time
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.db import SessionLocal
from app.models import Event, EventDelivery
from app.queue import (
    GROUP, STREAM, ack_and_cleanup, client, drain_due_retries, enqueue,
    enqueue_dlq, ensure_group, reclaim_idle, schedule_retry,
)
from app.reliability import backoff_seconds
from app.websocket import manager

class NoSubscribers(Exception):
    pass

async def publish_unpublished(limit: int = 50):
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Event).where(
                Event.status == 'queued', Event.published_at.is_(None)
            ).order_by(Event.created_at).limit(limit).with_for_update(skip_locked=True)
        )).scalars().all()
        for record in rows:
            payload={'id':record.id,'project_id':record.project_id,'type':record.event_type,
                     'payload':record.payload,'attempt':max(1,record.attempts+1)}
            try:
                await enqueue(payload)
                record.published_at=datetime.utcnow()
            except Exception as exc:
                record.last_error=str(exc)
        await s.commit()

async def _ensure_delivery_rows(s,event_id,project_id,client_ids):
    if not client_ids:
        return
    rows=[{
        'id':'dlv_'+uuid.uuid4().hex,
        'event_id':event_id,
        'project_id':project_id,
        'client_id':client_id,
        'status':'pending',
        'attempts':0,
    } for client_id in client_ids]
    stmt=insert(EventDelivery).values(rows).on_conflict_do_nothing(
        index_elements=['event_id','client_id']
    )
    await s.execute(stmt)

async def process(mid,fields):
    event=json.loads(fields['event'])
    eid=event['id']
    async with SessionLocal() as s:
        record=await s.get(Event,eid)
        if not record:
            await ack_and_cleanup(mid); return
        if record.status=='dead_letter':
            await ack_and_cleanup(mid); return
    recipients=await manager.clients(event['project_id'])
    if not recipients:
        raise NoSubscribers(f'no active subscribers for project {event["project_id"]}')
    client_ids=[cid for cid,_ in recipients]
    async with SessionLocal() as s:
        await _ensure_delivery_rows(s,eid,event['project_id'],client_ids)
        await s.commit()

    delivered,failed=await manager.broadcast(event['project_id'],{
        'event_id':eid,'type':event['type'],'payload':event['payload'],
        'status':'processed','attempt':event.get('attempt',1)
    })
    now=datetime.utcnow()
    async with SessionLocal() as s:
        for client_id in delivered:
            row=(await s.execute(select(EventDelivery).where(
                EventDelivery.event_id==eid,EventDelivery.client_id==client_id
            ))).scalar_one_or_none()
            if row:
                row.status='sent'; row.attempts+=1; row.delivered_at=now
        await s.execute(update(Event).where(Event.id==eid).values(
            status='delivered' if delivered else 'queued',
            attempts=event.get('attempt',1),last_error=None,
            next_attempt_at=None,delivered_at=now if delivered else None
        ))
        await s.commit()

    if not delivered:
        raise NoSubscribers(f'no clients accepted event {eid}')
    await ack_and_cleanup(mid)

async def process_entries(entries):
    for mid,fields in entries:
        try:
            await process(mid,fields)
        except NoSubscribers as exc:
            print(f'hamylion delivery pending: {exc}')
        except Exception as exc:
            print(f'hamylion worker error: {exc}')

async def main():
    await ensure_group()
    last_publish=0.0
    while True:
        try:
            now=time.time()
            if now-last_publish>=2:
                await publish_unpublished()
                await drain_due_retries()
                last_publish=now
            claimed=await reclaim_idle()
            if claimed and len(claimed)==2:
                await process_entries(claimed[1])
            messages=await client.xreadgroup(
                GROUP,settings.WORKER_NAME,{STREAM:'>'},count=20,block=5000
            )
            for _,entries in messages:
                await process_entries(entries)
        except Exception as exc:
            print(f'hamylion worker loop error: {exc}')
            await asyncio.sleep(2)

if __name__=='__main__':
    asyncio.run(main())
