from __future__ import annotations

import hashlib


def message_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def safe_event_log(event_id: str, chat_id: str, message_id: str, text: str) -> dict[str, str]:
    return {
        "event": "telegram_message_processed",
        "event_id": event_id,
        "chat_id": chat_id,
        "message_id": message_id,
        "text_fingerprint": message_fingerprint(text),
    }
