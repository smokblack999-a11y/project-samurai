from datetime import datetime
from sqlalchemy import String,Text,DateTime,Integer,UniqueConstraint
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
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    delivered_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    last_delivered_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    delivery_started_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True,index=True)
