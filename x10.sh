#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

case "${1:-scan}" in
  scan) python3 -m x10think.run scan ;;
  serve) python3 -m x10think.run serve ;;
  run) python3 -m x10think.run run ;;
  *) echo "Usage: $0 {scan|serve|run}" >&2; exit 2 ;;
esac
