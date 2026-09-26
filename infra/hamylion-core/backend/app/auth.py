import hashlib
from datetime import datetime, timezone
from fastapi import Header,HTTPException
from sqlalchemy import select, update

from .config import settings
from .db import SessionLocal
from .models import ApiKey

def _hash(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

async def validate_api_key(x_api_key: str | None = Header(default=None)):
    if not x_api_key:
        raise HTTPException(401,'Missing API key')

    # Development/bootstrap compatibility. Production should use DB-backed keys.
    if settings.API_KEY and x_api_key == settings.API_KEY:
        return 'default-project'

    async with SessionLocal() as s:
        key = (await s.execute(select(ApiKey).where(
            ApiKey.key_hash == _hash(x_api_key),
            ApiKey.active.is_(True),
        ))).scalar_one_or_none()
        if not key:
            raise HTTPException(401,'Invalid API key')
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if key.expires_at and key.expires_at <= now:
            raise HTTPException(401,'API key expired')
        await s.execute(update(ApiKey).where(ApiKey.id == key.id).values(last_used_at=now))
        await s.commit()
        return key.project_id
