# AgentCheck

AgentCheck is a defensive static assessment prototype for **Agent Production Readiness**.

It scans a local repository for observable signals around tool use, external content, approval boundaries, telemetry, retry policy, tests, CI, documentation and possible hard-coded secrets.

It does **not** exploit targets and does not claim that a score is a probability of safety.

## Run

```bash
python -m agentcheck ./path/to/agent --json report.json --html report.html
```

## Current scope

- Repository inventory
- Tool/function signal detection
- Approval-boundary signal detection
- External-content surface signal detection
- Telemetry/audit signal detection
- Retry/backoff signal detection
- Possible hard-coded credential detection
- Test/CI/documentation readiness
- JSON and HTML reports

## Product direction

`static scan -> evidence -> finding -> remediation -> verification -> regression checks`

The intended commercial product is a fixed-scope Agent Production Readiness assessment followed by optional remediation and continuous regression verification.
