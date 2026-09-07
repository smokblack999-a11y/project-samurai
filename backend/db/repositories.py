import json
import hashlib
from .database import connect


def _hash_items(items):
    payload = [item.model_dump(mode="json") for item in items]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def get_idempotent_response(key, items):
    request_hash = _hash_items(items)
    with connect() as conn:
        row = conn.execute(
            "SELECT request_hash, response_json FROM idempotency_keys WHERE key=?", (key,)
        ).fetchone()
    if not row:
        return None
    if row["request_hash"] != request_hash:
        raise ValueError("idempotency key was already used with a different request")
    return json.loads(row["response_json"])


def add_inventory(items, idempotency_key=None):
    response = {"confirmed": 0, "ids": [], "ledger_entries": 0}
    request_hash = _hash_items(items)
    with connect() as conn:
        if idempotency_key:
            existing = conn.execute(
                "SELECT request_hash, response_json FROM idempotency_keys WHERE key=?",
                (idempotency_key,),
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise ValueError("idempotency key was already used with a different request")
                return json.loads(existing["response_json"])

        for item in items:
            row = conn.execute(
                "SELECT id FROM inventory WHERE name=? AND currency=?",
                (item.name.strip(), item.currency),
            ).fetchone()
            if row:
                inventory_id = row["id"]
                conn.execute(
                    "UPDATE inventory SET quantity=quantity+?, unit_price_minor=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (item.quantity, item.unit_price_minor, inventory_id),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO inventory(name,quantity,unit_price_minor,currency) VALUES(?,?,?,?)",
                    (item.name.strip(), item.quantity, item.unit_price_minor, item.currency),
                )
                inventory_id = cur.lastrowid
            conn.execute(
                "INSERT INTO inventory_ledger(inventory_id,quantity_delta,unit_price_minor,currency,source,idempotency_key) VALUES(?,?,?,?,?,?)",
                (inventory_id, item.quantity, item.unit_price_minor, item.currency, "purchase_confirmation", idempotency_key),
            )
            response["ids"].append(inventory_id)
            response["confirmed"] += 1
            response["ledger_entries"] += 1

        if idempotency_key:
            conn.execute(
                "INSERT INTO idempotency_keys(key,request_hash,response_json) VALUES(?,?,?)",
                (idempotency_key, request_hash, json.dumps(response, separators=(",", ":"))),
            )
        conn.commit()
    return response


def list_inventory():
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM inventory ORDER BY updated_at DESC, id DESC"
        ).fetchall()]


def list_ledger(limit=200):
    limit = max(1, min(int(limit), 1000))
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            """SELECT l.*, i.name AS item_name
               FROM inventory_ledger l JOIN inventory i ON i.id=l.inventory_id
               ORDER BY l.id DESC LIMIT ?""", (limit,)
        ).fetchall()]
