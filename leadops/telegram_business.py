from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TelegramEvent:
    event_id: str
    connection_id: str
    chat_id: str
    message_id: str
    text: str
    source: str = "telegram_business"


def _text(message: dict[str, Any]) -> str:
    content = message.get("content") or {}
    if content.get("@type") == "messageText":
        return str((content.get("text") or {}).get("text") or "")
    return ""


def normalize_update(update: dict[str, Any]) -> TelegramEvent | None:
    if update.get("@type") != "updateBotNewBusinessMessage":
        return None
    connection_id = str(update.get("connection_id") or "")
    message = update.get("message") or {}
    chat_id = str(message.get("chat_id") or "")
    message_id = str(message.get("id") or "")
    if not connection_id or not chat_id or not message_id:
        return None
    return TelegramEvent(
        event_id=f"tg-business:{connection_id}:{chat_id}:{message_id}",
        connection_id=connection_id,
        chat_id=chat_id,
        message_id=message_id,
        text=_text(message),
    )
