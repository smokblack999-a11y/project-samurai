import uuid
from datetime import datetime
from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect,HTTPException,Response
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import select,update
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal,engine
from .models import Base,Event,Outbox
from .schemas import EventRequest,EventResponse
from .auth import validate_api_key,issue_ws_token,verify_ws_token
from .rate_limit import enforce_project_rate_limit
from prometheus_client import Counter,generate_latest,CONTENT_TYPE_LATEST
from .websocket import manager
from .config import settings
from .aegis import router as aegis_router

app=FastAPI(title='HAMYLION Core',version='4.2.0')
app.include_router(aegis_router)
HTTP_REQUESTS=Counter('hamylion_http_requests_total','HTTP requests',['method','path','status'])

def event_payload(eid,project_id,event_type,payload,**extra):
    data={'id':eid,'project_id':project_id,'type':event_type,'payload':payload}
    data.update(extra)
    return data

def add_outbox(session,eid,project_id,event_type,payload,**extra):
    session.add(Outbox(
        id='obx_'+uuid.uuid4().hex,
        event_id=eid,
        payload=event_payload(eid,project_id,event_type,payload,**extra),
    ))

@app.middleware('http')
async def collect_http_metrics(request,call_next):
    response=await call_next(request)
    route=request.scope.get('route')
    route_path=getattr(route,'path','unmatched')
    HTTP_REQUESTS.labels(request.method,route_path,str(response.status_code)).inc()
    return response

@app.get('/metrics')
async def metrics():
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)

@app.on_event('startup')
async def startup():
    # Schema changes are deployed through Alembic, not create_all.
    if settings.AUTO_CREATE_SCHEMA:
        async with engine.begin() as c:
            await c.run_sync(Base.metadata.create_all)

@app.get('/pilot',include_in_schema=False)
async def pilot_console():
    return FileResponse(Path(__file__).with_name('pilot.html'),media_type='text/html')

@app.get('/health')
async def health():
    return {'status':'ok','service':'hamylion-core','version':'4.2.0'}

@app.post('/v1/events',response_model=EventResponse)
async def create_event(req:EventRequest,project_id:str=Depends(enforce_project_rate_limit)):
    async with SessionLocal() as s:
        existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one_or_none()
        if existing:
            return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
        eid='evt_'+uuid.uuid4().hex
        e=Event(id=eid,project_id=project_id,event_type=req.type,idempotency_key=req.idempotency_key,payload=req.payload)
        s.add(e)
        add_outbox(s,eid,project_id,req.type,req.payload)
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()
            existing=(await s.execute(select(Event).where(Event.project_id==project_id,Event.idempotency_key==req.idempotency_key))).scalar_one()
            return EventResponse(event_id=existing.id,status=existing.status,replayed=True)
    return EventResponse(event_id=eid,status='queued')

@app.get('/v1/events/{event_id}')
async def get_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id))).scalar_one_or_none()
    if not e: raise HTTPException(404,'not_found')
    return {'event_id':e.id,'type':e.event_type,'payload':e.payload,'status':e.status,'attempts':e.attempts,'last_error':e.last_error,'created_at':e.created_at,'delivered_at':e.delivered_at,'retry_at':e.retry_at}

@app.post('/v1/events/{event_id}/ack')
async def ack_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        result=await s.execute(update(Event).where(Event.id==event_id,Event.project_id==project_id,Event.status!='delivered').values(status='delivered',delivered_at=datetime.utcnow(),last_delivered_at=datetime.utcnow(),last_error=None,retry_at=None))
        await s.commit()
        if result.rowcount==0:
            e=await s.get(Event,event_id)
            if not e or e.project_id!=project_id: raise HTTPException(404,'not_found')
    return {'event_id':event_id,'status':'delivered'}

@app.get('/v1/dlq')
async def list_dlq(project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        rows=(await s.execute(select(Event).where(Event.project_id==project_id,Event.status=='dead_letter').order_by(Event.created_at.desc()).limit(100))).scalars().all()
    return {'events':[{'event_id':e.id,'type':e.event_type,'attempts':e.attempts,'last_error':e.last_error,'created_at':e.created_at} for e in rows]}

@app.post('/v1/dlq/{event_id}/replay')
async def replay_dlq(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id,Event.status=='dead_letter'))).scalar_one_or_none()
        if not e: raise HTTPException(404,'not_found')
        e.status='queued'; e.last_error=None; e.retry_at=None; e.attempts=0
        add_outbox(s,e.id,e.project_id,e.event_type,e.payload,replay=True)
        await s.commit()
    return {'event_id':event_id,'status':'requeued'}

@app.post('/v1/events/{event_id}/replay')
async def replay_event(event_id:str,project_id:str=Depends(validate_api_key)):
    async with SessionLocal() as s:
        e=(await s.execute(select(Event).where(Event.id==event_id,Event.project_id==project_id))).scalar_one_or_none()
        if not e: raise HTTPException(404,'not_found')
        e.status='queued'; e.last_error=None; e.retry_at=None; e.attempts=0
        add_outbox(s,e.id,e.project_id,e.event_type,e.payload,replay=True)
        await s.commit()
    return {'event_id':event_id,'status':'requeued'}

@app.post('/v1/ws-token')
async def create_ws_token(project_id:str=Depends(enforce_project_rate_limit)):
    return {'token':issue_ws_token(project_id),'expires_in':60}

@app.websocket('/v1/ws')
async def ws(websocket:WebSocket,project_id:str,token:str):
    if not verify_ws_token(token,project_id):
        await websocket.close(code=1008); return
    await manager.connect(project_id,websocket)
    try:
        while True:
            message=await websocket.receive_json()
            if message.get('type')=='ack' and message.get('event_id'):
                async with SessionLocal() as s:
                    await s.execute(update(Event).where(Event.id==message['event_id'],Event.project_id==project_id).values(status='delivered',delivered_at=datetime.utcnow(),last_delivered_at=datetime.utcnow(),last_error=None,retry_at=None))
                    await s.commit()
    except WebSocketDisconnect:
        await manager.disconnect(project_id,websocket)
