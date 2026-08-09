# AgentCheck v2

Deterministic first-pass scanner for AI-agent production readiness.

## Design

AgentCheck separates evidence collection from interpretation. Rules report:

`RULE -> EVIDENCE -> SEVERITY -> CONFIDENCE -> IMPACT -> REMEDIATION -> VERIFICATION`

The scanner is static-only in v2. It does not claim to prove exploitability or production safety. High/critical findings are signals that require verification.

## Run

```bash
python -m agentcheck.cli scan .
python -m agentcheck.cli scan . --format json
python -m agentcheck.cli scan . --format html --html-out report.html
python -m agentcheck.cli scan . --strict
```

## Current rule families

- SEC-001 secret exposure
- ACCESS-001 tool authorization boundary
- TOOL-001 unrestricted execution surface
- TOOL-002 tool input validation
- TOOL-003 tool output validation
- APPROVAL-001 sensitive side-effect approval
- SIDEFX-001 idempotency/safety boundary
- INJECT-001 prompt/external-content trust boundary
- CONTENT-001 external content in agent data path
- AUDIT-001 audit logging
- ERROR-001 discarded exception paths
- RETRY-001 external-call timeout/deadline
- EVAL-001 evaluation harness
- REGRESSION-001 regression tests
- OBS-001 runtime observability

## Commercial boundary

This is an evidence-producing diagnostic layer, not a claim of complete security. The first commercial unit is a fixed-scope Agent Production Readiness Review. Continuous regression and CI enforcement are later layers.
