# HAMYLION Core

HAMYLION is the durable event/runtime core for X10THINC.

## Runtime contract

1. PostgreSQL is the source of durable event state.
2. Alembic owns schema lifecycle; the API and worker never create schema implicitly.
3. The migrate Compose service must complete successfully before API/worker startup.
4. /ready is false until the database reports the expected Alembic revision.
5. Redis is transport/recovery infrastructure, not the source of truth.
6. Production deployments must replace development database credentials and API-key defaults.

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

Do not use hm_dev_change_me outside local development.
