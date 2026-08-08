from __future__ import annotations

import os
from pathlib import Path


def scan(base: str | Path = ".") -> list[dict[str, str]]:
    root = Path(base)
    findings: list[dict[str, str]] = []
    env_hits = [k for k in os.environ if any(x in k.lower() for x in ("api_key", "secret", "token", "password"))]
    if env_hits:
        findings.append({"severity": "info", "id": "env-secrets", "message": "Sensitive-looking environment variables are present; do not expose them in reports."})

    for name in (".env", ".env.local"):
        candidate = root / name
        if candidate.exists():
            findings.append({"severity": "high", "id": "env-file", "message": f"Sensitive config file exists: {candidate}. Keep it out of version control."})

    return findings
