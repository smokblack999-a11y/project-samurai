from pydantic import BaseModel,Field
class EventRequest(BaseModel):
    type:str=Field(min_length=1,max_length=128); payload:dict; idempotency_key:str=Field(min_length=1,max_length=255)
class EventResponse(BaseModel): event_id:str; status:str; replayed:bool=False
