from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TelegramEvent:
    event_id: str
    chat_id: str
    message_id: str
    text: str
    sender_id: str | None = None


def normalize_update(update: dict[str, Any]) -> TelegramEvent | None:
    """Normalize a TDLib JSON update without coupling the AI layer to TDLib."""
    if update.get("@type") != "updateNewMessage":
        return None
    message = update.get("message") or {}
    content = message.get("content") or {}
    if content.get("@type") != "messageText":
        return None
    text = ((content.get("text") or {}).get("text") or "").strip()
    if not text:
        return None
    chat_id = str(message.get("chat_id", ""))
    message_id = str(message.get("id", ""))
    if not chat_id or not message_id:
        return None
    return TelegramEvent(
        event_id=f"tg:{chat_id}:{message_id}",
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        sender_id=str((message.get("sender_id") or {}).get("user_id")) if (message.get("sender_id") or {}).get("user_id") else None,
    )
