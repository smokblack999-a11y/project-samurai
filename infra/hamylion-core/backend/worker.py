import asyncio
import json
from datetime import datetime

from sqlalchemy import update

from app.config import settings
from app.db import SessionLocal
from app.models import Event
from app.queue import (
    GROUP,
    STREAM,
    client,
    drain_due_retries,
    enqueue_dlq,
    ensure_group,
    reclaim_idle,
    schedule_retry,
)
from app.reliability import backoff_seconds
from app.websocket import manager


async def process(mid, fields):
    event = json.loads(fields['event'])
    eid = event['id']

    async with SessionLocal() as s:
        record = await s.get(Event, eid)
        if not record:
            await client.xack(STREAM, GROUP, mid)
            return
        if record.status in {'delivered', 'dead_letter'}:
            await client.xack(STREAM, GROUP, mid)
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
                    )
                )
                await s.commit()
                retry_event = {**event, 'attempt': attempt + 1}
                await schedule_retry(retry_event, __import__('time').time() + delay)
        await client.xack(STREAM, GROUP, mid)
        return

    async with SessionLocal() as s:
        await s.execute(
            update(Event).where(Event.id == eid).values(
                status='delivered',
                attempts=attempt,
                delivered_at=datetime.utcnow(),
                last_error=None,
            )
        )
        await s.commit()

    await client.xack(STREAM, GROUP, mid)


async def process_entries(entries):
    for mid, fields in entries:
        try:
            await process(mid, fields)
        except Exception as exc:
            # Keep the worker alive; the message remains recoverable until ACKed.
            print(f'hamylion worker error: {exc}')


async def main():
    await ensure_group()
    while True:
        try:
            await drain_due_retries()

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
