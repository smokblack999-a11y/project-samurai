#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

checks = {
    "python3": sys.version_info >= (3, 10),
    "config": (BASE / "config.json").is_file(),
    "disk": shutil.disk_usage(BASE).free > 0,
    "openai_key": bool(os.getenv("OPENAI_API_KEY")),
}

for name, ok in checks.items():
    print(f"{'OK' if ok else 'WARN':<5} {name}")

if not checks["openai_key"]:
    print("WARN  OPENAI_API_KEY is not set; AI analysis will be disabled.")

print(json.dumps(checks, indent=2))
