# X10THINK Sentinel Security Model

## Trust boundaries

1. Telemetry, logs, retrieved text, and model output are untrusted.
2. The AI layer proposes analysis only; it does not authorize execution.
3. Policy classification is deny-by-default.
4. Sensitive or write actions require explicit operator/admin approval.
5. Executor re-checks policy before execution.
6. Approved actions carry a fingerprint and expiration time.
7. Execution is single-use and audited.

## Forbidden by default

- arbitrary shell execution
- destructive file operations
- privilege changes
- credential handling through model output

## Production requirements

- use strong randomly generated API keys or an external identity provider
- terminate TLS at a trusted boundary
- isolate the executor from the host when write actions are enabled
- rotate secrets and never commit them
- add rate limits and resource budgets
- run adversarial tests before enabling new tools
