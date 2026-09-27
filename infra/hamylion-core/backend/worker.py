import asyncio
import json
import time
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.db import SessionLocal
from app.models import Event, EventDelivery
from app.queue import (
    GROUP,
    STREAM,
    ack_and_cleanup,
    client,
    drain_due_retries,
    enqueue,
    enqueue_dlq,
    ensure_group,
    reclaim_idle,
    schedule_retry,
)
from app.reliability import backoff_seconds
from app.websocket import manager

class NoSubscribers(Exception):
    pass

async def publish_unpublished(limit: int = 50):
    async with SessionLocal() as s:
        rows = (
            await s.execute(
                select(Event)
                .where(Event.status == 'queued', Event.published_at.is_(None))
                .order_by(Event.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        ).scalars().all()

        for record in rows:
            payload = {
                'id': record.id,
                'project_id': record.project_id,
                'type': record.event_type,
                'payload': record.payload,
                'attempt': max(1, record.attempts + 1),
            }
            try:
                await enqueue(payload)
                record.published_at = datetime.utcnow()
            except Exception as exc:
                record.last_error = str(exc)
        await s.commit()

async def _ensure_delivery(s, event_id: str, project_id: str):
    delivery = (await s.execute(select(EventDelivery).where(
        EventDelivery.event_id == event_id,
        EventDelivery.project_id == project_id,
    ))).scalar_one_or_none()
    if delivery:
        return delivery
    delivery = EventDelivery(
        id='dlv_' + uuid.uuid4().hex,
        event_id=event_id,
        project_id=project_id,
        status='pending',
    )
    s.add(delivery)
    try:
        await s.flush()
    except IntegrityError:
        await s.rollback()
        delivery = (await s.execute(select(EventDelivery).where(
            EventDelivery.event_id == event_id,
            EventDelivery.project_id == project_id,
        ))).scalar_one()
    return delivery

async def process(mid, fields):
    event = json.loads(fields['event'])
    eid = event['id']

    async with SessionLocal() as s:
        record = await s.get(Event, eid)
        if not record:
            await ack_and_cleanup(mid)
            return
        if record.status == 'dead_letter':
            await ack_and_cleanup(mid)
            return
        delivery = await _ensure_delivery(s, eid, event['project_id'])
        if delivery.status == 'acked':
            await s.execute(update(Event).where(Event.id == eid).values(
                status='delivered',
                delivered_at=delivery.acked_at or datetime.utcnow(),
                attempts=max(record.attempts, 1),
            ))
            await s.commit()
            await ack_and_cleanup(mid)
            return

    delivered_clients = await manager.broadcast(
        event['project_id'],
        {
            'event_id': eid,
            'type': event['type'],
            'payload': event['payload'],
            'status': 'processed',
            'attempt': event.get('attempt', 1),
        },
    )
    if delivered_clients == 0:
        raise NoSubscribers(f'no active subscribers for project {event["project_id"]}')

    async with SessionLocal() as s:
        delivery = await _ensure_delivery(s, eid, event['project_id'])
        delivery.status = 'sent'
        delivery.attempts += 1
        delivery.last_sent_at = datetime.utcnow()
        await s.execute(update(Event).where(Event.id == eid).values(
            status='processed',
            attempts=max((await s.get(Event, eid)).attempts, event.get('attempt', 1)),
            last_error=None,
            next_attempt_at=None,
        ))
        await s.commit()

    await ack_and_cleanup(mid)

async def process_entries(entries):
    for mid, fields in entries:
        try:
            await process(mid, fields)
        except NoSubscribers as exc:
            print(f'hamylion delivery pending: {exc}')
        except Exception as exc:
            print(f'hamylion worker error: {exc}')

async def main():
    await ensure_group()
    last_publish = 0.0
    while True:
        try:
            now = time.time()
            if now - last_publish >= 2:
                await publish_unpublished()
                await drain_due_retries()
                last_publish = now

            claimed = await reclaim_idle()
            if claimed and len(claimed) == 2:
                await process_entries(claimed[1])

            messages = await client.xreadgroup(
                GROUP,
                settings.WORKER_NAME,
                {STREAM: '>'},
                count=20,
                block=5000,
            )
            for _, entries in messages:
                await process_entries(entries)
        except Exception as exc:
            print(f'hamylion worker loop error: {exc}')
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(main())
