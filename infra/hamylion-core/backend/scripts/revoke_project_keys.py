"""Revoke all active keys for a project without exposing their plaintext values."""
import argparse
import asyncio
from sqlalchemy import update
from app.db import SessionLocal
from app.models import ApiKey

async def revoke(project_id: str) -> int:
    async with SessionLocal() as session:
        result = await session.execute(
            update(ApiKey)
            .where(ApiKey.project_id == project_id, ApiKey.active.is_(True))
            .values(active=False)
        )
        await session.commit()
        return result.rowcount or 0

def main():
    parser = argparse.ArgumentParser(description="Revoke active HAMYLION API keys")
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()
    count = asyncio.run(revoke(args.project_id))
    print(f"Revoked {count} active key(s) for {args.project_id}")

if __name__ == "__main__":
    main()
