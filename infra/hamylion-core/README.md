# HAMYLION Core 4.2 — AEGIS

Reliable event-ingestion foundation plus an optional, evidence-first defensive security analysis gateway.

## AEGIS

POST /v1/security/analyze accepts one bounded source-code, configuration, log, or incident-notes artifact. It requires the project's existing X-API-Key and returns schema-validated findings with severity, confidence, evidence, impact, remediation, assumptions, safe regression tests, and scope warnings.

Example request:

    {
      "artifact_type": "source_code",
      "task": "code_review",
      "context": "Owned repository; review this function only.",
      "content": "def check_access(user): ..."
    }

### AEGIS safety and data handling

- No model tools, shell, browser, network scanner, exploit runner, or autonomous remediation are exposed.
- Artifact and context are treated as untrusted data; embedded instructions are ignored.
- Common credential patterns and private-key blocks are redacted before provider submission.
- Raw submitted artifacts and model outputs are not written to the HAMYLION database by AEGIS.
- Provider request uses store=false and a pseudonymous project-level safety_identifier.
- Request size is capped at 20,000 characters; context at 2,000 characters; provider timeout is bounded.
- Responses must satisfy a strict JSON Schema and are validated again by Pydantic.
- AI is advisory only. Findings require human verification; no automatic changes or tests are executed.
- The service fails closed when provider credentials are absent or model access is unavailable.

### Daybreak boundary

AEGIS_CYBER_PROGRAM defaults to standard. Daybreak Blue/Red can only be selected when AEGIS_INTERNAL_SECURITY_ONLY=true is explicitly configured by the operator for an approved internal security workspace. Do not route customer-facing, downstream, or third-party traffic through Daybreak. OpenAI organization approval, project enablement, model approval, and model/program compatibility are still required. This environment flag is an operator attestation, not an access grant.

The default model is gpt-6-sol; set AEGIS_MODEL to a model actually enabled for the API project. A failed or unauthorized provider request does not silently downgrade to a different model.

## Existing Core

PostgreSQL remains the source of truth. Event + outbox are committed atomically; Redis Streams dispatch is at-least-once; consumers must be idempotent. WebSocket fanout remains in-memory per API process. See deployment runbook and integration-test limitations before production use.

## Local run

1. Copy .env.example to .env.
2. Set unique values for HAMYLION_API_KEY, WS_TOKEN_SECRET, and POSTGRES_PASSWORD.
3. Optionally set OPENAI_API_KEY to enable AEGIS.
4. Run docker compose up --build.

Alembic runs before API startup. Schema auto-creation is disabled by default.
