# HAMYLION AEGIS — Design Partner Pilot

## Pilot goal

Evaluate whether AEGIS helps a small software team triage code/configuration risks faster than its current manual review process. This is a bounded assistant, not a penetration test, source-control integration, compliance certificate, or replacement for SAST/DAST/security review.

## Pilot scope

- One participating engineering team.
- Up to 3 sanitized source/configuration artifacts per session; each request is limited to 20,000 characters.
- Review tasks: code review, configuration review, incident triage, or threat modeling.
- Output: findings with severity, confidence, evidence, impact, remediation, CWE, and safe test suggestions.
- Static heuristics currently detect eval, subprocess with shell=True, verify=False, DEBUG=True, and likely hard-coded credentials.
- Standard OpenAI API model only. Daybreak is disabled for customer pilot traffic in this build.

## Customer prerequisites

1. Written permission to submit the selected artifacts.
2. Explicit approval for external AI processing.
3. Use a test or sanitized artifact first. Do not submit production secrets, personal data, customer records, private keys, or regulated data.
4. Review the applicable OpenAI API data controls and your organization's contract/retention requirements before submitting proprietary code.
5. Provide a technical reviewer to verify or reject findings.

The API enforces both authorized_to_submit=true and external_ai_processing_approved=true on every request. These flags capture a caller attestation; they do not replace a contract, DPA, lawful basis, or internal approval.

## Run locally

1. Copy .env.example to .env.
2. Set strong unique values for HAMYLION_API_KEY, WS_TOKEN_SECRET, and POSTGRES_PASSWORD.
3. Add an OpenAI API key from a project that has access to the selected model. Keep AEGIS_CYBER_PROGRAM=standard.
4. Start services: docker compose up --build -d.
5. Provision a dedicated pilot project/key: docker compose exec api python scripts/provision_project.py --name "Design Partner Pilot". Store the generated key in a secret manager; never send it by email.
6. Use that generated project key for every pilot request. The global HAMYLION_API_KEY is reserved for legacy/internal compatibility.
7. Check health: curl http://localhost:8000/health.
8. Run tests: docker compose exec api python -m pytest -q.
9. Submit the synthetic fixture before any customer artifact.

## Browser console

After deployment, open `/pilot` on the same origin as the API. The console keeps the project API key in the current page memory only and does not write it to localStorage. Load the synthetic sample first.

Choose Static-only to call `POST /v1/security/static-scan`. This mode runs the built-in heuristics and does not call an external AI provider; it still requires the caller to attest that they are authorized to submit the artifact.

Choose AI + static review to call `POST /v1/security/analyze`. This additionally requires the explicit external-AI-processing approval checkbox and a configured OpenAI API project/model.

## Synthetic smoke test

Use examples/pilot_sample.py. It contains only fake, deliberately risky sample code. Submit its contents to POST /v1/security/analyze with:

- artifact_type=source_code
- task=code_review
- authorized_to_submit=true
- external_ai_processing_approved=true

Expected deterministic signals:
- eval(...) — AEGIS-PY-001
- verify=False — AEGIS-TLS-001
- hard-coded dummy API value — AEGIS-SECRET-001

The smoke test passes only when these three deterministic signals appear and the dummy secret value never appears in returned evidence. The model may add or omit other findings; manually inspect them.

## Pilot acceptance criteria

A pilot is accepted only after the customer and HAMYLION reviewer agree that:

- All three seeded static signals are found.
- The original dummy secret value is never returned in evidence.
- Each finding is attributable to static_rule or model_review.
- The model does not claim the code was executed or the system was scanned.
- At least 5 customer-reviewed real findings (or false positives) are recorded to assess usefulness.
- No artifact is sent without explicit customer approval.
- All limitations and false positives are documented before expanding scope.

Measure response time, cost per request, reviewer agreement, false-positive rate, and time saved. Do not publish delivery or detection-rate claims from a tiny pilot.

## Data handling

- Ask the client to provide a synthetic or sanitized fixture first.
- Never request production secrets, private keys, customer records, or regulated data.
- Do not accept a full private repository until written approval, data-processing terms, and retention settings have been reviewed.
- store=false does not guarantee Zero Data Retention; check the actual OpenAI API project settings and applicable contract.
- Provision a dedicated project key and revoke it at the end of the pilot if the customer does not continue.

## Pilot closeout

At the end of the pilot, share:
- number of artifacts reviewed;
- model/static findings by severity;
- reviewer-confirmed findings;
- false positives and missed seeded issues;
- median and p95 response time;
- approximate provider cost;
- customer feedback and decision to continue, revise, or stop.
