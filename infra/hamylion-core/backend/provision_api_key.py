"""Provision a project-scoped HAMYLION API key.

Run inside the backend image after migrations:
    python provision_api_key.py PROJECT_ID [NAME]

The secret is printed once. Only its SHA-256 hash is persisted.
"""
from __future__ import annotations

import asyncio
import hashlib
import secrets
import sys
import uuid

from sqlalchemy import insert

from app.db import SessionLocal
from app.models import ApiKey

async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python provision_api_key.py PROJECT_ID [NAME]")
    project_id = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "default"
    token = "hm_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    async with SessionLocal() as session:
        await session.execute(insert(ApiKey).values(
            id="key_" + uuid.uuid4().hex,
            project_id=project_id,
            name=name,
            key_hash=key_hash,
            active=True,
        ))
        await session.commit()

    print(token)

if __name__ == "__main__":
    asyncio.run(main())
