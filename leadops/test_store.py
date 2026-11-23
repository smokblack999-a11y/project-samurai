from store import EventStore


def test_duplicate_event_is_ignored(tmp_path):
    store = EventStore(str(tmp_path / "events.db"))
    assert store.put("tg:1:2", "1", "2", "hello", "{}") is True
    assert store.seen("tg:1:2") is True
    assert store.put("tg:1:2", "1", "2", "hello", "{}") is False
