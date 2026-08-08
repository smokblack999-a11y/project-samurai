# X10THINK Sentinel

A local-first infrastructure health agent with guarded AI diagnostics.

## Run

```bash
cd x10think
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='YOUR_EXISTING_KEY'
python doctor.py
python -m uvicorn api:app --host 127.0.0.1 --port 7010
```

Open `http://127.0.0.1:7010/`.

## API

- `GET /status` — compact status
- `GET /health` — telemetry and findings
- `POST /scan` — health plus optional AI analysis
- `POST /analyze` — analyze supplied telemetry
- `POST /action?name=health` — allow-listed local action

The application never stores an API key in the repository. Use the existing `OPENAI_API_KEY` environment variable locally. OpenAI is optional: without the key, health checks still work.

## Safety boundary

The first release deliberately does not expose arbitrary shell execution to the AI. Actions must be explicitly allow-listed in `core.py`. This is a product requirement, not an implementation detail.
