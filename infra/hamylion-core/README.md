# HAMYLION Core

HAMYLION is the durable event/runtime core for X10THINC.

## Runtime contract

1. PostgreSQL is the source of durable event state.
2. Alembic owns schema lifecycle; the API and worker never create schema implicitly.
3. The migrate Compose service must complete successfully before API/worker startup.
4. /ready is false until the database reports the expected Alembic revision.
5. Redis is transport/recovery infrastructure, not the source of truth.
6. Production deployments must replace development database credentials and API-key defaults.
7. Redis Streams are transport only; they are never the sole durable copy of an event.
8. Production API authentication uses database-backed, project-scoped keys; the environment key is bootstrap compatibility only.
9. GitHub webhooks must use an explicit repository allowlist when more than one repository can share infrastructure.

## Local run

    export HAMYLION_API_KEY='replace-me'
    docker compose up --build

Schema migrations are applied by the migrate service. The API becomes ready only after revision 0001_events is applied.

## Production gate

Before exposing the service publicly, configure:

- a managed PostgreSQL instance and non-default credentials;
- a project-scoped API-key store/rotation mechanism;
- explicit outbound host allowlists;
- a real GitHub webhook secret;
- required CI/security checks on the deployment repository.

Provision a project-scoped key after migration with `python provision_api_key.py PROJECT_ID NAME`; the plaintext token is emitted once and only its SHA-256 hash is persisted.

Do not use `hm_dev_change_me` outside local development.
