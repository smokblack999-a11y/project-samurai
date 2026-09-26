# HAMYLION Core 3.0

Durable realtime event infrastructure for X10THINC and other projects.

PostgreSQL is the source of truth; Redis Streams is the asynchronous transport. Events have project scope, idempotency keys, durable status, retry/error tracking and replay/recovery hooks. WebSocket is a delivery surface, not the database.

## Run
`docker compose up --build`

## API
`POST /v1/events` with `type`, `payload`, `idempotency_key` and `X-API-Key`.

## Architecture
Producer -> API -> PostgreSQL -> Redis Stream -> Worker -> WebSocket/Webhook adapters.

## X10THINC
X10THINC can publish normalized GitHub/Fireflies/HubSpot/Notion signals into HAMYLION instead of coupling its reasoning engine to a transport implementation.

## Production gate
Before claiming guaranteed delivery: add destination ACKs, exponential backoff with bounded attempts, DLQ, multi-tenant project/key storage, rate limits, metrics/tracing, encrypted secrets, migrations, and automated crash/restart/duplicate/replay tests.
