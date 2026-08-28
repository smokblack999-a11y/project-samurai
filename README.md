# Telegram LeadOps AI

Commercial MVP for turning inbound Telegram messages into prioritized lead decisions.

## Product outcome

A business operator should see which incoming Telegram conversations deserve attention first and what action to take.

## Architecture

`Telegram/TDLib -> event normalizer -> FastAPI -> OpenAI decision engine -> persistence -> dashboard/API`

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
uvicorn app.main:app --reload --port 8000
```

OpenAPI: `http://127.0.0.1:8000/docs`

Health: `GET /health`

Analysis: `POST /api/v1/analyze/message`

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze/message \
  -H 'Content-Type: application/json' \
  -d '{"message_id":"demo-1","text":"Сколько стоит заказать услугу?"}'
```

Never commit API keys. The OpenAI integration requires `OPENAI_API_KEY` at runtime.
