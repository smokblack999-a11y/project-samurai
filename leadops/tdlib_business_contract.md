# TDLib Business contract

Telegram Business supports connected bots that can process business-account messages. The integration boundary should accept normalized events only.

Required normalized fields:
- event_id
- connection_id
- chat_id
- message_id
- text
- received_at

The adapter must reject events without message identity and must never forward credentials to the AI layer.

For connected business bots, Telegram exposes business connection identifiers and bot rights; production implementation must follow the current TDLib layer rather than hard-coded legacy schemas.
