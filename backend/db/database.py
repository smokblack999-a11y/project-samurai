import sqlite3
from pathlib import Path
from core.config import get_settings


def db_path():
    url = get_settings().database_url
    if not url.startswith("sqlite:///"):
        raise RuntimeError("MVP currently supports only sqlite DATABASE_URL")
    return url.replace("sqlite:///", "", 1)


def connect():
    conn = sqlite3.connect(db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def _add_column_if_missing(conn, table, column, definition):
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    Path(db_path()).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT,
            quantity REAL NOT NULL,
            unit_price_minor INTEGER NOT NULL,
            sale_price_minor INTEGER,
            currency TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, currency)
        )""")
        _add_column_if_missing(conn, "inventory", "sale_price_minor", "INTEGER")
        _add_column_if_missing(conn, "inventory", "sku", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_inventory_sku_currency ON inventory(sku, currency)")
        conn.execute("""CREATE TABLE IF NOT EXISTS inventory_ledger(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER NOT NULL,
            quantity_delta REAL NOT NULL,
            unit_price_minor INTEGER NOT NULL,
            currency TEXT NOT NULL,
            source TEXT NOT NULL,
            idempotency_key TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(inventory_id) REFERENCES inventory(id)
        )""")
        conn.execute("""CREATE UNIQUE INDEX IF NOT EXISTS ux_inventory_ledger_idem
            ON inventory_ledger(idempotency_key) WHERE idempotency_key IS NOT NULL""")
        conn.execute("""CREATE TABLE IF NOT EXISTS idempotency_keys(
            key TEXT PRIMARY KEY,
            request_hash TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
