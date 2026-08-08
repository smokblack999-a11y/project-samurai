# API Lifecycle Safety

## Outcome
Know when it is safe to retire a legacy API without causing a downstream outage.

## Inputs
- OpenAPI specification
- production access logs
- replacement endpoint health
- migration progress
- Sunset header metadata

## Outputs
- SAFE / REVIEW / BLOCKED decision
- consumer evidence
- unknown traffic risk
- remediation actions
- reproducible evidence fingerprint

## Product boundary
The deterministic engine owns the decision. AI may explain evidence and propose remediation, but it must not override policy or approve shutdown.

## Pilot
Run one legacy API audit and deliver an evidence-backed report.
