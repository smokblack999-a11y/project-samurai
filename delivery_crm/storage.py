from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


class DeliveryStore:
    STATUSES = {"awaiting_details", "payment_review", "approved", "assigned", "delivered", "rejected"}

    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        parent = Path(self.db_path).parent
        if not parent.exists():
            parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    customer_name TEXT NOT NULL,
                    details TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    receipt_file_id TEXT,
                    status TEXT NOT NULL,
                    courier_id INTEGER,
                    delivery_photo_file_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_delivery_orders_status ON orders(status)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_delivery_orders_customer ON orders(customer_id)")

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=10)
        try:
            if os.name == "posix":
                os.chmod(self.db_path, 0o600)
        except OSError:
            db.close()
            raise
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def create_order(self, customer_id: int, customer_name: str, details: str, phone: str, address: str) -> int:
        with self._connect() as db:
            cur = db.execute(
                """INSERT INTO orders(customer_id,customer_name,details,phone,address,status)
                   VALUES(?,?,?,?,?,'awaiting_details')""",
                (customer_id, customer_name[:128], details[:2000], phone[:40], address[:500]),
            )
            return int(cur.lastrowid)

    def submit_receipt(self, order_id: int, customer_id: int, file_id: str) -> bool:
        with self._connect() as db:
            cur = db.execute(
                """UPDATE orders SET receipt_file_id=?,status='payment_review',updated_at=CURRENT_TIMESTAMP
                   WHERE id=? AND customer_id=? AND status='awaiting_details'""",
                (file_id, order_id, customer_id),
            )
            return cur.rowcount == 1

    def get_order(self, order_id: int) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
            return dict(row) if row else None

    def list_orders(self, status: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as db:
            if status:
                rows = db.execute("SELECT * FROM orders WHERE status=? ORDER BY id", (status,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 50").fetchall()
            return [dict(row) for row in rows]

    def approve(self, order_id: int) -> bool:
        with self._connect() as db:
            cur = db.execute(
                "UPDATE orders SET status='approved',updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='payment_review' AND receipt_file_id IS NOT NULL",
                (order_id,),
            )
            return cur.rowcount == 1

    def reject(self, order_id: int) -> bool:
        with self._connect() as db:
            cur = db.execute(
                "UPDATE orders SET status='rejected',updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='payment_review'",
                (order_id,),
            )
            return cur.rowcount == 1

    def assign(self, order_id: int, courier_id: int) -> bool:
        with self._connect() as db:
            cur = db.execute(
                "UPDATE orders SET status='assigned',courier_id=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='approved'",
                (courier_id, order_id),
            )
            return cur.rowcount == 1

    def mark_delivered(self, order_id: int, courier_id: int, photo_file_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            cur = db.execute(
                """UPDATE orders SET status='delivered',delivery_photo_file_id=?,updated_at=CURRENT_TIMESTAMP
                   WHERE id=? AND courier_id=? AND status='assigned'""",
                (photo_file_id, order_id, courier_id),
            )
            if cur.rowcount != 1:
                return None
            row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
            return dict(row)
