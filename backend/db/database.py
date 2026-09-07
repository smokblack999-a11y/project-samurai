import sqlite3
from pathlib import Path
from core.config import get_settings

def db_path():
    return get_settings().database_url.replace("sqlite:///", "")

def connect():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    Path(db_path()).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,quantity REAL NOT NULL,unit_price_minor INTEGER NOT NULL,currency TEXT NOT NULL)")
        conn.commit()
