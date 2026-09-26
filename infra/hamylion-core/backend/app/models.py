from datetime import datetime
from sqlalchemy import String,Text,DateTime,Integer,UniqueConstraint,Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase): pass

class Event(Base):
    __tablename__='events'
    __table_args__=(UniqueConstraint('project_id','idempotency_key',name='uq_event_idempotency'),)

    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    project_id:Mapped[str]=mapped_column(String(128),index=True)
    event_type:Mapped[str]=mapped_column(String(128),index=True)
    idempotency_key:Mapped[str]=mapped_column(String(255),index=True)
    payload:Mapped[dict]=mapped_column(JSONB)
    status:Mapped[str]=mapped_column(String(32),default='queued',index=True)
    attempts:Mapped[int]=mapped_column(Integer,default=0)
    last_error:Mapped[str|None]=mapped_column(Text,nullable=True)
    next_attempt_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True,index=True)
    published_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    updated_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    delivered_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    dead_lettered_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)

class ApiKey(Base):
    __tablename__='api_keys'
    __table_args__=(UniqueConstraint('key_hash',name='uq_api_key_hash'),)

    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    project_id:Mapped[str]=mapped_column(String(128),index=True)
    name:Mapped[str]=mapped_column(String(128))
    key_hash:Mapped[str]=mapped_column(String(64),index=True)
    active:Mapped[bool]=mapped_column(Boolean,default=True,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    expires_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    last_used_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
