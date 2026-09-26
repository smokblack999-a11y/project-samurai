from fastapi import Header,HTTPException
from .config import settings
def validate_api_key(x_api_key:str|None=Header(default=None)):
    if not settings.API_KEY: raise HTTPException(500,'HAMYLION_API_KEY is not configured')
    if x_api_key!=settings.API_KEY: raise HTTPException(401,'Invalid API key')
    return 'default-project'
