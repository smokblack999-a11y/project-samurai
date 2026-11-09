"""Provision a project-scoped HAMYLION API key.

Run inside the API container after Alembic migrations:
  python scripts/provision_project.py --name "Pilot partner"

The raw key is printed once. Store it in the client's secret manager.
Only its SHA-256 hash is persisted.
"""
import argparse
import asyncio
import hashlib
import secrets
import uuid

from sqlalchemy import select

from app.db import SessionLocal
from app.models import ApiKey, Project


async def provision(name: str, project_id: str | None = None) -> tuple[str, str]:
    project_id = project_id or ("proj_" + uuid.uuid4().hex)
    raw_key = "hm_live_" + secrets.token_urlsafe(36)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    async with SessionLocal() as session:
        existing = await session.get(Project, project_id)
        if existing:
            raise SystemExit(f"Project already exists: {project_id}")
        session.add(Project(id=project_id, name=name))
        session.add(ApiKey(
            id="key_" + uuid.uuid4().hex,
            project_id=project_id,
            key_hash=key_hash,
            active=True,
        ))
        await session.commit()
    return project_id, raw_key


def main():
    parser = argparse.ArgumentParser(description="Create a HAMYLION project and one API key")
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--project-id", default=None, help="Optional stable project ID")
    args = parser.parse_args()
    project_id, api_key = asyncio.run(provision(args.name, args.project_id))
    print("Project provisioned.")
    print(f"PROJECT_ID={project_id}")
    print(f"API_KEY={api_key}")
    print("Save the API key now; it cannot be retrieved in plaintext.")
    print("Do not paste it into chat, source control, or email.")


if __name__ == "__main__":
    main()
