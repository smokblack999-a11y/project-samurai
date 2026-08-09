#!/usr/bin/env bash
set -euo pipefail

BASE="${X10THINK_URL:-http://127.0.0.1:7010}"

printf '\n[1] status\n'
curl -fsS "$BASE/status"
printf '\n[2] health\n'
curl -fsS "$BASE/health"
printf '\n[3] scan\n'
curl -fsS -X POST "$BASE/scan"
printf '\n[demo complete]\n'
