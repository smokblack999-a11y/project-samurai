# Telegram ingest contract

The Telegram adapter must normalize TDLib updates into the internal message shape:

```json
{"message_id":"tg:123:456","chat_id":"123","text":"..."}
```

Requirements:

1. Never pass raw TDLib objects into the business layer.
2. Use a stable event/message identifier.
3. Ignore unsupported update types safely.
4. Make ingestion idempotent.
5. Do not log authorization credentials, phone numbers, tokens, or message content by default.
6. Human approval remains required for outbound actions in the MVP.
