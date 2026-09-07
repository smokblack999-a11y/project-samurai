import json
import hashlib
from .database import connect
from domain.economics import margin_percent, profit_minor


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
            name = " ".join(item.name.split())
            currency = item.currency.upper()
            row = conn.execute(
                "SELECT id FROM inventory WHERE name=? AND currency=?",
                (name, currency),
            ).fetchone()
            if row:
                inventory_id = row["id"]
                conn.execute(
                    "UPDATE inventory SET quantity=quantity+?, unit_price_minor=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (item.quantity, item.unit_price_minor, inventory_id),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO inventory(name,quantity,unit_price_minor,sale_price_minor,currency) VALUES(?,?,?,?,?)",
                    (name, item.quantity, item.unit_price_minor, None, currency),
                )
                inventory_id = cur.lastrowid
            conn.execute(
                "INSERT INTO inventory_ledger(inventory_id,quantity_delta,unit_price_minor,currency,source,idempotency_key) VALUES(?,?,?,?,?,?)",
                (inventory_id, item.quantity, item.unit_price_minor, currency, "purchase_confirmation", idempotency_key),
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


def set_sale_price(inventory_id, sale_price_minor):
    with connect() as conn:
        row = conn.execute("SELECT id FROM inventory WHERE id=?", (inventory_id,)).fetchone()
        if not row:
            raise ValueError("inventory item not found")
        conn.execute(
            "UPDATE inventory SET sale_price_minor=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (sale_price_minor, inventory_id),
        )
        conn.commit()
    return {"updated": True, "id": inventory_id, "sale_price_minor": sale_price_minor}


def dashboard():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id,name,quantity,unit_price_minor,sale_price_minor,currency FROM inventory ORDER BY name COLLATE NOCASE"
        ).fetchall()
    items = []
    total_cost = 0
    total_profit = 0
    for row in rows:
        sale = row["sale_price_minor"]
        cost = int(row["unit_price_minor"])
        margin = margin_percent(cost, int(sale)) if sale is not None and sale > 0 else None
        profit = profit_minor(cost, int(sale), row["quantity"]) if sale is not None and sale > 0 else None
        total_cost += round(cost * row["quantity"])
        if profit is not None:
            total_profit += profit
        items.append({
            "id": row["id"],
            "name": row["name"],
            "quantity": row["quantity"],
            "cost_minor": cost,
            "sale_price_minor": sale,
            "currency": row["currency"],
            "margin_percent": margin,
            "profit_minor": profit,
        })
    return {
        "items": items,
        "total_stock_cost_minor": total_cost,
        "total_expected_profit_minor": total_profit,
    }
