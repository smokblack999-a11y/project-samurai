# HAMYLION Core 4.3 — AEGIS Pilot

Reliable event-ingestion foundation plus an optional, evidence-first defensive security analysis gateway.

## AEGIS API

POST /v1/security/analyze accepts one bounded source-code, configuration, log, or incident-notes artifact. It requires a project-scoped X-API-Key and both attestations: authorized_to_submit=true and external_ai_processing_approved=true.

Response fields include risk_level, findings, severity, confidence, evidence, impact, remediation, CWE, assumptions, recommended_tests, and scope_warnings.

Example request body:

~~~json
{
  "artifact_type": "source_code",
  "task": "code_review",
  "context": "Review this owned test fixture only.",
  "content": "def check_access(user): ...",
  "authorized_to_submit": true,
  "external_ai_processing_approved": true
}
~~~

## What AEGIS currently does

- Calls the OpenAI Responses API with strict Structured Outputs.
- Runs deterministic heuristic checks alongside the model for eval, subprocess shell=True, verify=False, DEBUG=True, and likely hard-coded credentials.
- Labels each finding as model_review or static_rule.
- Redacts common credential patterns and private keys before provider submission. This is heuristic redaction, not complete DLP.
- Uses store=false and a pseudonymous project-level safety_identifier.
- Applies a separate Redis-backed project rate limit (default 10 analyses/minute).
- Does not expose model tools, shell, browser, remote scanning, exploit execution, or automatic remediation.
- Does not persist submitted artifacts or reports in the HAMYLION database.
- Requires human verification of all findings.

Important data note: store=false requests non-persistence of the Responses object. It does not itself guarantee Zero Data Retention or replace a DPA, lawful basis, internal approval, or contractual review. Confirm the OpenAI API project's retention settings before sending proprietary or personal data.

## Daybreak boundary

AEGIS_CYBER_PROGRAM defaults to standard. Daybreak Blue/Red in this build is restricted to allowlisted internal project IDs and an explicit internal-only operator flag. It is not enabled for this customer pilot. OpenAI organization approval, project enablement, model approval, and model/program compatibility are separate requirements. The environment flag is an operator restriction, not an access grant.

The default model is gpt-6-sol. Set AEGIS_MODEL only to a model enabled for the API project. A failed or unauthorized request does not silently downgrade to a different model.

## Customer project and API-key provisioning

After Alembic migrations have run:

~~~bash
docker compose exec api python scripts/provision_project.py --name "Pilot Customer"
~~~

The command prints a new project ID and a randomly generated API key exactly once. The database stores only the SHA-256 hash. Store the plaintext key in a secret manager and deliver it through an approved secure channel, never email or source control.

To revoke active keys for a project:

~~~bash
docker compose exec api python scripts/revoke_project_keys.py --project-id PROJECT_ID
~~~

The legacy HAMYLION_API_KEY remains as a compatibility fallback for the internal SAMURAI bridge. Do not give that global key to a pilot customer.

## Local run

1. Copy .env.example to .env.
2. Set unique strong values for HAMYLION_API_KEY, WS_TOKEN_SECRET, and POSTGRES_PASSWORD.
3. Add OPENAI_API_KEY from a project that can call the selected model. Keep AEGIS_CYBER_PROGRAM=standard.
4. Run docker compose up --build -d.
5. Check http://localhost:8000/health.
6. Provision a dedicated project key as described above.
7. Run tests with docker compose exec api python -m pytest -q.
8. Submit examples/pilot_sample.py before customer artifacts.

## Current limitations

- Built-in deterministic checks are intentionally small heuristics, not a comprehensive SAST engine.
- No Semgrep/Bandit full SAST integration, DAST, dependency graph scan, malware analysis, or network scanning.
- No GitHub/GitLab repository integration or automatic PR comments.
- No automatic patching or command execution.
- No full PostgreSQL/Redis crash integration suite or load test has been completed in this branch.
- No live OpenAI call has been validated until an operator configures credentials and tests the exact project/model access.
- WebSocket fanout remains in-memory per API process.
- Daybreak access is not assumed and is not enabled for this pilot.

See PILOT.md for scope, customer prerequisites, smoke test, and acceptance criteria.
