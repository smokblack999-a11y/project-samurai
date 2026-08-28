# Telegram LeadOps AI

Commercial MVP for turning inbound Telegram messages into prioritized lead decisions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

OpenAPI: `http://127.0.0.1:8000/docs`

Health: `GET /health`

Analysis: `POST /api/v1/analyze/message`

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze/message \
  -H 'Content-Type: application/json' \
  -d '{"text":"Сколько стоит заказать услугу?"}'
```

The current classifier is intentionally deterministic. OpenAI integration must pass the evaluation suite before replacing the baseline.
