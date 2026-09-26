import asyncio
import json
import time
import uuid
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.db import SessionLocal
from app.models import Delivery, Event, WebSocketClient
from app.queue import GROUP, STREAM, ack_and_cleanup, client, drain_due_retries, enqueue, ensure_group, reclaim_idle

from app.websocket import manager

async def publish_unpublished(limit=50):
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Event).where(Event.status=='queued',Event.published_at.is_(None))
            .order_by(Event.created_at).limit(limit).with_for_update(skip_locked=True)
        )).scalars().all()
        for record in rows:
            try:
                await enqueue({'id':record.id,'project_id':record.project_id,'type':record.event_type,'payload':record.payload,'attempt':max(1,record.attempts+1)})
                record.published_at=datetime.utcnow()
            except Exception as exc:
                record.last_error=str(exc)
        await s.commit()

async def materialize_deliveries(event):
    async with SessionLocal() as s:
        clients=(await s.execute(
            select(WebSocketClient).where(WebSocketClient.project_id==event['project_id'])
        )).scalars().all()
        for client in clients:
            s.add(Delivery(
                id='del_'+uuid.uuid4().hex,
                event_id=event['id'],
                project_id=event['project_id'],
                client_id=client.id,
                status='pending',
            ))
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()

async def deliver_pending():
    async with SessionLocal() as s:
        rows=(await s.execute(
            select(Delivery).where(Delivery.status=='pending')
            .order_by(Delivery.created_at).limit(100)
        )).scalars().all()

    for delivery in rows:
        connection=await manager.find(delivery.project_id,delivery.client_id)
        if not connection:
            continue
        async with SessionLocal() as s:
            event=await s.get(Event,delivery.event_id)
        if not event:
            continue
        try:
            await connection.websocket.send_json({
                'delivery_id':delivery.id,
                'event_id':event.id,
                'type':event.event_type,
                'payload':event.payload,
            })
            async with SessionLocal() as s:
                await s.execute(update(Delivery).where(
                    Delivery.id==delivery.id,Delivery.status=='pending'
                ).values(
                    status='delivered',
                    attempts=Delivery.attempts+1,
                    delivered_at=datetime.utcnow(),
                    last_error=None,
                ))
                await s.commit()
        except Exception as exc:
            await manager.disconnect(delivery.project_id,delivery.client_id)
            async with SessionLocal() as s:
                await s.execute(update(Delivery).where(Delivery.id==delivery.id).values(
                    attempts=Delivery.attempts+1,last_error=str(exc)
                ))
                await s.commit()

async def process(mid,fields):
    event=json.loads(fields['event'])
    eid=event['id']
    async with SessionLocal() as s:
        record=await s.get(Event,eid)
        if not record:
            await ack_and_cleanup(mid)
            return
        if record.status=='dead_letter':
            await ack_and_cleanup(mid)
            return

    await materialize_deliveries(event)

    async with SessionLocal() as s:
        await s.execute(update(Event).where(Event.id==eid).values(
            status='processed',attempts=Event.attempts+1,last_error=None
        ))
        await s.commit()
    await ack_and_cleanup(mid)

async def process_entries(entries):
    for mid,fields in entries:
        try:
            await process(mid,fields)
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
                await deliver_pending()
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
