# Telegram LeadOps AI — pilot

Purpose: turn inbound Telegram-style messages into a ranked lead decision and a human next action.

## Run

```bash
cd leadops
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='your-existing-key'
uvicorn app:app --host 127.0.0.1 --port 8000
```

Then use `/docs` or:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze/message -H 'Content-Type: application/json' -d '{"text":"Сколько стоит заказать сегодня?"}'
```

## Commercial gate

Do not build more UI before testing with real businesses. Target 10 qualified prospects -> 5 demos -> 3 pilots -> 1 paid pilot.

## Safety

The pilot does not send autonomous Telegram messages. It produces a decision for a human operator. Never commit API keys.
