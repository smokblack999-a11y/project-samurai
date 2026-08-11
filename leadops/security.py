from __future__ import annotations


def safe_event_log(event_id: str, chat_id: str, message_id: str) -> dict[str, str]:
    return {"event": "telegram_message_processed", "event_id": event_id, "chat_id": chat_id, "message_id": message_id}


def redact_text(text: str, limit: int = 120) -> str:
    compact = " ".join(text.split())
    return compact[:limit] + ("…" if len(compact) > limit else "")
