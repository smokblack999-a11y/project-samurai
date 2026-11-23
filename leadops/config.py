from __future__ import annotations

import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {"1", "true", "yes", "on"}

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
DB_PATH = os.getenv("LEADOPS_DB", "leadops.db")
AI_ENABLED = bool(os.getenv("OPENAI_API_KEY"))
OUTBOUND_ENABLED = env_bool("LEADOPS_OUTBOUND_ENABLED", False)
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "12"))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000"))
MAX_NEEDS = int(os.getenv("MAX_NEEDS", "20"))
