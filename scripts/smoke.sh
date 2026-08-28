#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8090}"
go test ./...
(go run ./cmd/server >/tmp/samurai-server.log 2>&1 & echo $! >/tmp/samurai-server.pid)
trap 'kill "$(cat /tmp/samurai-server.pid)" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null; then break; fi
  sleep 0.2
done
curl -fsS "http://127.0.0.1:${PORT}/api/system/status"
echo
