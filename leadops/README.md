# Telegram LeadOps AI — pilot

Purpose: turn inbound Telegram-style messages into a ranked lead decision and a human next action.

## Run

```bash
cd leadops
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
export OPENAI_API_KEY='your-existing-key'
uvicorn app:app --host 127.0.0.1 --port 8000
```

Never commit the real key. Keep it in the local environment or an approved secret manager.

## Validation

```bash
make test
make evaluate
make benchmark
make report
```

Use `/docs` for the API contract. `/api/v1/ingest/telegram` accepts a normalized TDLib-style update and deduplicates by event ID.

## Product wedge

Do not compete as a generic Telegram CRM. The first commercial offer is a bounded diagnostic: identify high-intent conversations, missed-priority patterns, response-time baseline, and conservative ROI.

## Commercial gate

Target: 10 qualified prospects -> 5 demos -> 3 pilots -> 1 paid pilot.

Before claiming production accuracy, replace synthetic cases with at least 100 anonymized, authorized real messages and measure precision, recall, F1, false positives, latency, and cost per message.

## Safety

The pilot does not send autonomous Telegram messages. It produces a decision for a human operator. Never commit API keys, Telegram sessions, bot tokens, or raw customer exports.
