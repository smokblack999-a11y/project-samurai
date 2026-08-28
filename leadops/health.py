from __future__ import annotations

import os


def snapshot() -> dict[str, bool]:
    return {
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "outbound_enabled": os.getenv("LEADOPS_OUTBOUND_ENABLED", "false").lower() == "true",
    }
