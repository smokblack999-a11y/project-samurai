from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    token: str
    admin_ids: frozenset[int]
    price_text: str
    payment_instructions: str
    db_path: str

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
        raw_admins = os.getenv("DELIVERY_ADMIN_IDS", "")
        try:
            admin_ids = frozenset(int(x.strip()) for x in raw_admins.split(",") if x.strip())
        except ValueError as exc:
            raise RuntimeError("DELIVERY_ADMIN_IDS must contain numeric Telegram IDs") from exc
        if not admin_ids:
            raise RuntimeError("At least one DELIVERY_ADMIN_IDS entry is required")
        price = os.getenv("DELIVERY_PRICE_TEXT", "").strip()
        payment = os.getenv("DELIVERY_PAYMENT_INSTRUCTIONS", "").strip()
        if not price or not payment:
            raise RuntimeError("DELIVERY_PRICE_TEXT and DELIVERY_PAYMENT_INSTRUCTIONS are required")
        return cls(
            token=token,
            admin_ids=admin_ids,
            price_text=price,
            payment_instructions=payment,
            db_path=os.getenv("DELIVERY_DB_PATH", "delivery_crm.sqlite3"),
        )
