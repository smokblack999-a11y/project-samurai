import asyncio,json
from sqlalchemy import update
from app.db import SessionLocal
from app.models import Event
from app.queue import client,STREAM,GROUP,ensure_group,reclaim_idle
from app.config import settings
from app.websocket import manager

async def process(mid,fields):
    event=json.loads(fields['event']); eid=event['id']
    async with SessionLocal() as s:
        e=await s.get(Event,eid)
        if not e:
            await client.xack(STREAM,GROUP,mid); return
        if e.status=='delivered':
            await client.xack(STREAM,GROUP,mid); return
        if e.attempts>=settings.MAX_RETRIES:
            await s.execute(update(Event).where(Event.id==eid).values(status='dead_letter',last_error='max_retries_exceeded'))
            await s.commit(); await client.xack(STREAM,GROUP,mid); return
        await s.execute(update(Event).where(Event.id==eid).values(status='delivering',attempts=Event.attempts+1,last_error=None))
        await s.commit()
    await manager.broadcast(event['project_id'],{'event_id':eid,'type':event['type'],'payload':event['payload'],'status':'delivering'})
    await client.xack(STREAM,GROUP,mid)

async def main():
    await ensure_group()
    while True:
        try:
            await reclaim_idle()
            messages=await client.xreadgroup(GROUP,'worker-1',{STREAM:'>'},count=20,block=5000)
            for _,entries in messages:
                for mid,fields in entries:
                    try: await process(mid,fields)
                    except Exception as exc:
                        event=json.loads(fields['event'])
                        async with SessionLocal() as s:
                            await s.execute(update(Event).where(Event.id==event['id']).values(status='retrying',last_error=str(exc)))
                            await s.commit()
        except Exception:
            await asyncio.sleep(2)

if __name__=='__main__': asyncio.run(main())
