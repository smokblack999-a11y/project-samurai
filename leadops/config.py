from __future__ import annotations

import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {"1", "true", "yes", "on"}

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
DB_PATH = os.getenv("LEADOPS_DB", "leadops.db")
AI_ENABLED = bool(os.getenv("OPENAI_API_KEY"))
OUTBOUND_ENABLED = env_bool("LEADOPS_OUTBOUND_ENABLED", False)
