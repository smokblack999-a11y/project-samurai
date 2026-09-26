# HAMYLION Core 3.1

Durable realtime event infrastructure for X10THINC and other projects.

## Architecture

Producer -> API -> PostgreSQL -> Redis Stream -> Worker -> WebSocket/Webhook adapters.

PostgreSQL is the durable source of truth. Redis Streams is the asynchronous transport. The implementation now includes:

- project-scoped idempotency keys;
- durable publication marker / outbox recovery;
- bounded exponential retry with durable Redis ZSET scheduling;
- stale consumer recovery with XAUTOCLAIM;
- explicit dead-letter stream;
- replay endpoint;
- readiness endpoint;
- signed GitHub webhook ingestion using X-Hub-Signature-256;
- GitHub delivery deduplication through X-GitHub-Delivery;
- worker identity configuration;
- reliability unit tests and CI syntax checks.

## API

POST /v1/events with type, payload, idempotency_key and X-API-Key.

GET /v1/events/{event_id} returns durable processing state.

POST /v1/events/{event_id}/replay requeues a stored event for operator recovery.

POST /v1/github/webhook accepts signed GitHub webhook deliveries and uses the GitHub delivery GUID as the idempotency key.

GET /health is liveness; GET /ready checks database readiness.

## X10THINC

X10THINC can publish normalized GitHub/Fireflies/HubSpot/Notion signals into HAMYLION instead of coupling its reasoning engine to a transport implementation.

## Production gate

This hardening layer still does **not** by itself constitute an enterprise production deployment. Remaining work includes:

1. database migrations instead of create_all at startup;
2. real multi-tenant API-key records with rotation/revocation and hashed storage;
3. rate limiting at the API edge;
4. outbound destination registry with per-destination ACK state and SSRF-safe allowlisting;
5. OpenTelemetry traces/metrics/log correlation;
6. encrypted secret storage / secret manager integration;
7. durable WebSocket delivery semantics where required by the product;
8. integration tests covering crash/restart, duplicate delivery, replay, DLQ recovery and PostgreSQL/Redis failure;
9. GitHub App installation lifecycle and least-privilege permission enforcement;
10. sandboxed repair execution and X10THINK/Kill Critic verification before autonomous repository changes.

Never claim guaranteed delivery or autonomous remediation until those gates are verified in the deployed environment.
