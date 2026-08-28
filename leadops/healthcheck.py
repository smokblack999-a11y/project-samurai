from __future__ import annotations

import os


def readiness() -> dict[str, bool]:
    return {
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "outbound_disabled": os.getenv("LEADOPS_OUTBOUND_ENABLED", "false").lower() != "true",
        "db_path_configured": bool(os.getenv("LEADOPS_DB", "leadops.db")),
    }


if __name__ == "__main__":
    print(readiness())
