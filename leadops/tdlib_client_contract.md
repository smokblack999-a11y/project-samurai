# TDLib integration boundary

The LeadOps API must not depend on TDLib C++ internals. A TDLib process/client emits JSON updates; `telegram_adapter.py` normalizes only the supported `updateNewMessage -> messageText` path.

Production flow:

1. TDLib receives Telegram updates.
2. Adapter forwards each update to `POST /api/v1/ingest/telegram`.
3. LeadOps derives deterministic `event_id = tg:<chat_id>:<message_id>`.
4. SQLite uniqueness prevents duplicate processing.
5. The decision is persisted with the event.
6. High-value messages produce `human_followup`; this MVP never sends outbound Telegram messages automatically.

Security rules:

- Telegram credentials stay in the TDLib adapter environment.
- `OPENAI_API_KEY` stays in the API service environment and is never committed.
- Message text is not logged by default.
- Event IDs must be deterministic and unique.
- The adapter owns TDLib authorization state.
- The API owns business decisions and persistence.
- Outbound Telegram actions remain disabled until human-approved pilot validation.
