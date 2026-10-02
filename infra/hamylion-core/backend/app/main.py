import uuid
from datetime import datetime
from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect,HTTPException
from sqlalchemy import select,update
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal,engine
from .models import Base,Event
from .schemas import EventRequest,EventResponse
from .auth import validate_api_key
from .queue import enqueue
from .websocket import manager
from .config import settings

app=FastAPI(title='HAMYLION Core',version='4.0.0')

@app.on_event('startup')
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)

@app.get('/health')
async def health(): return {'status':'ok','service':'hamylion-core','version':'4.0.0'}

@app.post('/v1/events',response_model=EventResponse)
async def create_event(req:EventRequest,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one_or_none()
        if existing: return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
        eid='evt_'+uuid.uuid4().hex
        e=Event(id=eid,project_id=project_id,event_type=req.type,idempotency_key=req.idempotency_key,payload=req.payload)
        s.add(e)
        try: await s.commit()
        except IntegrityError:
            await s.rollback()
            existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one()
            return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
    await enqueue({'id':eid,'project_id':project_id,'type':req.type,'payload':req.payload})
    return EventResponse(event_id=eid,status='queued')

@app.get('/v1/events/{event_id}')
async def get_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id))).scalar_one_or_none()
    if not e: raise HTTPException(404,'not_found')
    return {'event_id':e.id,'type':e.event_type,'payload':e.payload,'status':e.status,'attempts':e.attempts,'last_error':e.last_error,'created_at':e.created_at,'delivered_at':e.delivered_at}

@app.post('/v1/events/{event_id}/ack')
async def ack_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        result=await s.execute(update(Event).where(Event.id==event_id,Event.project_id==project_id,Event.status!='delivered').values(status='delivered',delivered_at=datetime.utcnow(),last_delivered_at=datetime.utcnow(),last_error=None))
        await s.commit()
    if result.rowcount==0:
        async with SessionLocal() as s: e=await s.get(Event,event_id)
        if not e or e.project_id!=project_id: raise HTTPException(404,'not_found')
    return {'event_id':event_id,'status':'delivered'}

@app.post('/v1/events/{event_id}/replay')
async def replay_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id))).scalar_one_or_none()
    if not e: raise HTTPException(404,'not_found')
    await enqueue({'id':e.id,'project_id':e.project_id,'type':e.event_type,'payload':e.payload,'replay':True})
    return {'event_id':e.id,'status':'requeued'}

@app.websocket('/v1/ws')
async def ws(websocket:WebSocket,project_id:str,api_key:str):
    if not settings.API_KEY or api_key!=settings.API_KEY:
        await websocket.close(code=1008); return
    await manager.connect(project_id,websocket)
    try:
        while True:
            message=await websocket.receive_json()
            if message.get('type')=='ack' and message.get('event_id'):
                async with SessionLocal() as s:
                    await s.execute(update(Event).where(Event.id==message['event_id'],Event.project_id==project_id).values(status='delivered',delivered_at=datetime.utcnow(),last_delivered_at=datetime.utcnow(),last_error=None))
                    await s.commit()
    except WebSocketDisconnect:
        await manager.disconnect(project_id,websocket)
