#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 doctor.py
python3 -m uvicorn api:app --host "${X10_HOST:-127.0.0.1}" --port "${X10_PORT:-7010}"
