import uuid
from datetime import datetime
from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal,engine
from .models import Base,Event
from .schemas import EventRequest,EventResponse
from .auth import validate_api_key
from .queue import enqueue
from .websocket import manager
app=FastAPI(title='HAMYLION Core',version='3.0.0')
@app.on_event('startup')
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
@app.get('/health')
async def health(): return {'status':'ok','service':'hamylion-core','version':'3.0.0'}
@app.post('/v1/events',response_model=EventResponse)
async def create_event(req:EventRequest,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one_or_none()
        if existing: return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
        eid='evt_'+uuid.uuid4().hex; e=Event(id=eid,project_id=project_id,event_type=req.type,idempotency_key=req.idempotency_key,payload=req.payload)
        s.add(e)
        try: await s.commit()
        except IntegrityError: await s.rollback(); existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one(); return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
    await enqueue({'id':eid,'project_id':project_id,'type':req.type,'payload':req.payload})
    return EventResponse(event_id=eid,status='queued')
@app.get('/v1/events/{event_id}')
async def get_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s: e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id))).scalar_one_or_none()
    if not e:return {'error':'not_found'}
    return {'event_id':e.id,'type':e.event_type,'payload':e.payload,'status':e.status,'attempts':e.attempts,'last_error':e.last_error,'created_at':e.created_at,'delivered_at':e.delivered_at}
@app.websocket('/v1/ws')
async def ws(websocket:WebSocket,project_id:str='default-project'):
    await manager.connect(project_id,websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: await manager.disconnect(project_id,websocket)
