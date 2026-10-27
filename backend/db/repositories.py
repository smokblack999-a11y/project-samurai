import difflib
import json
import hashlib
import re
from .database import connect
from domain.economics import margin_percent, profit_minor


def _hash_items(items):
    payload = [item.model_dump(mode="json") for item in items]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _normalize_name(value):
    value = value.casefold().replace("ё", "е")
    return re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE).strip()


def _name_score(left, right):
    a = _normalize_name(left)
    b = _normalize_name(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    at = set(a.split())
    bt = set(b.split())
    token = len(at & bt) / max(1, len(at | bt))
    return round(max(ratio, token), 4)


def match_inventory_items(items, top_k=3):
    with connect() as conn:
        inventory = [dict(row) for row in conn.execute(
            "SELECT id,name,sku,currency FROM inventory ORDER BY name COLLATE NOCASE"
        ).fetchall()]

    results = []
    for item in items:
        name = " ".join(item.name.split())
        currency = item.currency.upper()
        candidates = []
        for row in inventory:
            if row["currency"].upper() != currency:
                continue
            if item.sku and row.get("sku") and item.sku.strip().casefold() == row["sku"].strip().casefold():
                score = 1.0
                reason = "exact_sku"
            else:
                score = _name_score(name, row["name"])
                reason = "name_similarity"
            if score >= 0.55:
                candidates.append({
                    "inventory_id": row["id"],
                    "name": row["name"],
                    "sku": row.get("sku"),
                    "score": score,
                    "reason": reason,
                })
        candidates.sort(key=lambda x: (x["score"], x["reason"] == "exact_sku"), reverse=True)
        candidates = candidates[:top_k]
        best = candidates[0]["score"] if candidates else 0.0
        decision = "auto_match" if best >= 0.92 else "review_match" if best >= 0.75 else "new_product"
        results.append({
            "input_name": name,
            "input_sku": item.sku,
            "candidates": candidates,
            "decision": decision,
        })
    return results


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
            sku = item.sku.strip() if item.sku else None
            row = None
            if sku:
                row = conn.execute(
                    "SELECT id FROM inventory WHERE sku=? AND currency=?",
                    (sku, currency),
                ).fetchone()
            if not row:
                row = conn.execute(
                    "SELECT id FROM inventory WHERE name=? AND currency=?",
                    (name, currency),
                ).fetchone()
            if row:
                inventory_id = row["id"]
                conn.execute(
                    "UPDATE inventory SET quantity=quantity+?, unit_price_minor=?, sku=COALESCE(?,sku), updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (item.quantity, item.unit_price_minor, sku, inventory_id),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO inventory(name,sku,quantity,unit_price_minor,sale_price_minor,currency) VALUES(?,?,?,?,?,?)",
                    (name, sku, item.quantity, item.unit_price_minor, None, currency),
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
