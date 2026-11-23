from __future__ import annotations

import sqlite3
from pathlib import Path


class EventStore:
    def __init__(self, path: str = "leadops.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                text TEXT NOT NULL,
                decision_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()

    def seen(self, event_id: str) -> bool:
        row = self.db.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone()
        return row is not None

    def put(self, event_id: str, chat_id: str, message_id: str, text: str, decision_json: str | None = None) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO events(event_id,chat_id,message_id,text,decision_json) VALUES(?,?,?,?,?)",
            (event_id, chat_id, message_id, text, decision_json),
        )
        self.db.commit()
        return cur.rowcount == 1

    def update_decision(self, event_id: str, decision_json: str) -> None:
        self.db.execute("UPDATE events SET decision_json=? WHERE event_id=?", (decision_json, event_id))
        self.db.commit()
