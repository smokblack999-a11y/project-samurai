import asyncio
import json
import time
from datetime import datetime

from sqlalchemy import select, update

from app.config import settings
from app.db import SessionLocal
from app.models import Event
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

async def process(mid, fields):
    event = json.loads(fields['event'])
    eid = event['id']

    async with SessionLocal() as s:
        record = await s.get(Event, eid)
        if not record:
            await ack_and_cleanup(mid)
            return
        if record.status in {'delivered', 'dead_letter'}:
            await ack_and_cleanup(mid)
            return
        attempt = record.attempts + 1

    try:
        await manager.broadcast(
            event['project_id'],
            {
                'event_id': eid,
                'type': event['type'],
                'payload': event['payload'],
                'status': 'delivered',
                'attempt': attempt,
            },
        )
    except Exception as exc:
        async with SessionLocal() as s:
            if attempt >= settings.MAX_RETRIES:
                await s.execute(
                    update(Event).where(Event.id == eid).values(
                        status='dead_letter',
                        attempts=attempt,
                        last_error=str(exc),
                        dead_lettered_at=datetime.utcnow(),
                    )
                )
                await s.commit()
                await enqueue_dlq(event, str(exc))
            else:
                delay = backoff_seconds(
                    attempt, settings.RETRY_BASE_SECONDS, settings.RETRY_MAX_SECONDS
                )
                await s.execute(
                    update(Event).where(Event.id == eid).values(
                        status='retrying',
                        attempts=attempt,
                        last_error=str(exc),
                        next_attempt_at=datetime.fromtimestamp(time.time() + delay),
                    )
                )
                await s.commit()
                await schedule_retry({**event, 'attempt': attempt + 1}, time.time() + delay)
        await ack_and_cleanup(mid)
        return

    async with SessionLocal() as s:
        await s.execute(
            update(Event).where(Event.id == eid).values(
                status='delivered',
                attempts=attempt,
                delivered_at=datetime.utcnow(),
                last_error=None,
                next_attempt_at=None,
            )
        )
        await s.commit()

    await ack_and_cleanup(mid)

async def process_entries(entries):
    for mid, fields in entries:
        try:
            await process(mid, fields)
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
