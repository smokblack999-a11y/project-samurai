# HAMYLION Core 4.1

Reliable event-ingestion and delivery foundation for realtime applications.

PostgreSQL is the source of truth. The transactional outbox records publication intent in the same database transaction as each event. A worker dispatches outbox rows to Redis Streams. WebSocket is currently the implemented delivery adapter; webhook delivery is not implemented yet.

## Local run

1. Copy `.env.example` to `.env`.
2. Set unique values for `HAMYLION_API_KEY`, `WS_TOKEN_SECRET`, and `POSTGRES_PASSWORD`.
3. Run `docker compose up --build`.

The API container runs `alembic upgrade head` before starting. Schema auto-creation is disabled by default.

## Event API

Send `POST /v1/events` with `type`, `payload`, and `idempotency_key`, plus `X-API-Key`.

- `GET /v1/events/{event_id}` — inspect event status.
- `POST /v1/events/{event_id}/ack` — destination acknowledgement.
- `POST /v1/events/{event_id}/replay` — replay an event.
- `GET /v1/dlq` — list dead-letter events.
- `POST /v1/dlq/{event_id}/replay` — replay a dead-letter event.
- `POST /v1/ws-token` — mint a 60-second, project-scoped WebSocket token.
- `GET /metrics` — Prometheus HTTP request counters.
- `GET /health` — liveness endpoint.

## Delivery flow

`Producer -> API -> PostgreSQL(Event + Outbox, one transaction) -> Outbox dispatcher -> Redis Streams -> Worker -> WebSocket`

Retry scheduling is stored in PostgreSQL using `retry_at`; retries are re-enqueued through the outbox. Redis pending messages are reclaimed by the worker. Delivery status remains pending until a destination ACK or timeout recovery.

## Operational controls

- Project-scoped API keys are stored as SHA-256 hashes.
- Per-project fixed-window Redis rate limit; configure `RATE_LIMIT_PER_MINUTE`.
- WebSocket uses short-lived signed tokens, not the long-lived API key in its query string.
- Alembic owns schema changes.
- GitHub Actions runs unit tests and Python compilation checks.

## Important limitations

This is not yet a production-certified "exactly once" or "guaranteed delivery" system. Outbox dispatch is at-least-once; consumers must be idempotent. WebSocket fanout is in-memory per API process. There is no webhook adapter, distributed tracing, billing, API-key management endpoint, or full PostgreSQL/Redis crash integration suite. The legacy static API key remains as a compatibility fallback for the SAMURAI bridge.

Before a paid production pilot, run the Docker/PostgreSQL/Redis kill tests, verify duplicate handling and ACK timeout behavior, provision per-project keys, configure secret rotation, and test multi-instance delivery.
