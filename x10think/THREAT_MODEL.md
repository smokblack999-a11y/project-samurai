# X10THINK Sentinel MVP threat model

## Assets
- infrastructure state
- operator credentials
- OpenAI API key
- approval records
- audit history

## Threats
- prompt injection through telemetry/logs
- unauthorized action execution
- replay of an old approval
- privilege escalation
- secret leakage
- CI workflow compromise

## Controls
- untrusted telemetry boundary
- explicit action policy
- role-based approval
- short-lived approval records
- executor policy re-check
- append-only audit events
- minimal GitHub Actions permissions
- no secrets committed to the repository

## Out of scope for MVP
- arbitrary shell execution
- autonomous destructive remediation
- multi-tenant production isolation
