from __future__ import annotations

from .schemas import NormalizedMessage


def normalize_telegram_message(
    *,
    account_id: str,
    chat_id: int | str,
    message_id: int | str,
    text: str,
    received_at: int,
) -> NormalizedMessage:
    return NormalizedMessage(
        source="telegram",
        account_id=str(account_id),
        chat_id=str(chat_id),
        message_id=str(message_id),
        text=text.strip(),
        received_at=received_at,
    )
