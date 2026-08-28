# Operator Runbook

1. Start the API with a local `OPENAI_API_KEY`.
2. Verify `GET /health`.
3. Send a synthetic message to `/api/v1/analyze/message`.
4. Send a normalized Telegram update to `/api/v1/ingest/telegram`.
5. Repeat the same Telegram event and verify `duplicate=true`.
6. Review stored decisions before any customer-facing action.
7. Keep `LEADOPS_OUTBOUND_ENABLED=false` during the pilot.
8. Export evaluation metrics only from labeled data.
9. Never paste API keys into GitHub, issues, logs, or chat.
10. Record pilot results in the scorecard.
