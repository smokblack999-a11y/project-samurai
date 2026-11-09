# HAMYLION AEGIS — Design Partner Pilot

## Pilot goal

Evaluate whether AEGIS helps a small software team triage code/configuration risks faster than its current manual review process. This is a bounded assistant, not a penetration test, source-control integration, compliance certificate, or replacement for SAST/DAST/security review.

## Pilot scope

- One participating engineering team.
- Up to 3 sanitized source/configuration artifacts per session; each request is limited to 20,000 characters.
- Review tasks: code review, configuration review, incident triage, or threat modeling.
- Output: findings with severity, confidence, evidence, impact, remediation, CWE, and safe test suggestions.
- Static heuristics currently detect eval, subprocess with shell=True, verify=False, DEBUG=True, and likely hard-coded credentials. Other issues depend on model review.
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
5. Check health: curl http://localhost:8000/health.
6. Run tests: docker compose exec api python -m pytest -q.
7. Submit the synthetic fixture below before any customer artifact.

## Synthetic smoke test

Use the intentionally flawed, synthetic file examples/pilot_sample.py. It contains no real credential or customer data. Submit its contents to POST /v1/security/analyze with:

- artifact_type=source_code
- task=code_review
- authorized_to_submit=true
- external_ai_processing_approved=true

Expected deterministic signals:
- eval(...) — AEGIS-PY-001
- verify=False — AEGIS-TLS-001
- hard-coded dummy API value — AEGIS-SECRET-001

The smoke test passes only when the three deterministic signals appear with redacted evidence. The model may add or omit other findings; manually inspect them.

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

## Current technical limits

- No GitHub/GitLab repository connection or automatic PR comments.
- No Semgrep/Bandit full SAST engine yet; the built-in rules are a small heuristic set.
- No DAST, dependency graph scan, malware analysis, or network scanning.
- No automatic patching or command execution.
- No live model call has been validated merely by passing unit tests.
- store=false requests non-persistence of the Responses object; it does not by itself guarantee Zero Data Retention. Confirm the actual API project's retention settings and contractual terms.
- Static heuristics can produce false positives and miss vulnerabilities.
- Customer pilot must use standard model access unless a separate, documented product-embedding approval is obtained for any Cyber model/program.

## Pilot closeout

At the end of the pilot, share:
- number of artifacts reviewed;
- model/static findings by severity;
- reviewer-confirmed findings;
- false positives and missed seeded issues;
- median and p95 response time;
- approximate provider cost;
- customer feedback and decision to continue, revise, or stop.
