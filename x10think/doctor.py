#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

together_key = bool(os.getenv("TOGETHER_API_KEY"))
openai_key = bool(os.getenv("OPENAI_API_KEY"))

checks = {
    "python3": sys.version_info >= (3, 10),
    "config": (BASE / "config.json").is_file(),
    "disk": shutil.disk_usage(BASE).free > 0,
    "ai_provider_key": together_key or openai_key,
}

for name, ok in checks.items():
    print(f"{'OK' if ok else 'WARN':<5} {name}")

if not checks["ai_provider_key"]:
    print("WARN  Neither TOGETHER_API_KEY nor OPENAI_API_KEY is set; AI analysis will be disabled.")
else:
    providers = []
    if together_key:
        providers.append("together")
    if openai_key:
        providers.append("openai")
    print(f"OK    AI providers configured: {', '.join(providers)}")

print(json.dumps(checks, indent=2))
