from pathlib import Path

from x10think.health import score, snapshot
from x10think.security import scan
from x10think.store import Store


def test_health_snapshot_has_valid_score():
    current = snapshot()
    assert 0 <= score(current) <= 100


def test_store_roundtrip(tmp_path: Path):
    store = Store(tmp_path)
    store.write({"score": 91})
    assert store.read()["score"] == 91


def test_security_scan_returns_list():
    assert isinstance(scan("."), list)
