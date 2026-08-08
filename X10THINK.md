# X10THINK Sentinel

X10THINK is a local-first infrastructure intelligence MVP. It collects basic health telemetry, performs conservative security checks, exposes a small HTTP API, and can optionally send telemetry to OpenAI for diagnosis.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
./x10.sh scan
./x10.sh serve
```

Open `http://127.0.0.1:7010/` for the operator dashboard.

## AI analysis

Set an existing key in the environment; never commit it to Git:

```bash
export OPENAI_API_KEY='...'
export X10_OPENAI_MODEL='gpt-5-mini'
```

The analyzer is deliberately advisory. It does not execute model-generated shell commands. Any future remediation executor must use an explicit allowlist and approval gate.

## API

- `GET /api/status` — current stored state
- `GET /api/health` — run a fresh health/security scan
- `GET /api/logs` — reserved log endpoint

## Commercial direction

The MVP is intentionally narrow: diagnose infrastructure state and turn findings into actionable reports. The fastest validation path is a paid audit/setup service before building a multi-tenant SaaS.
