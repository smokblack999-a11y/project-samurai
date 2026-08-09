# TDLib integration boundary

The LeadOps API must not depend on TDLib C++ internals. A TDLib process/client emits JSON updates; `telegram_adapter.py` normalizes only the supported `updateNewMessage -> messageText` path.

Production flow:

1. TDLib receives Telegram updates.
2. Adapter forwards each update to `POST /api/v1/ingest/telegram`.
3. LeadOps derives deterministic `event_id = tg:<chat_id>:<message_id>`.
4. SQLite uniqueness prevents duplicate processing.
5. The decision is persisted with the event.
6. High-value messages produce `human_followup`; this MVP never sends outbound Telegram messages automatically.

This boundary lets TDLib be replaced or upgraded without changing the business decision engine.
