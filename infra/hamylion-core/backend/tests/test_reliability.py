from app.reliability import backoff_seconds, event_fingerprint, sign_payload, verify_signature


def test_backoff_is_bounded():
    assert backoff_seconds(1, 2, 10) == 2
    assert backoff_seconds(2, 2, 10) == 4
    assert backoff_seconds(5, 2, 10) == 10
    assert backoff_seconds(10, 2, 10) == 10


def test_fingerprint_is_stable():
    event = {"type": "demo", "payload": {"b": 2, "a": 1}}
    assert event_fingerprint(event) == event_fingerprint({"payload": {"a": 1, "b": 2}, "type": "demo"})


def test_webhook_signature():
    body = b'{"ok":true}'
    sig = sign_payload("secret", body)
    assert verify_signature("secret", body, sig)
    assert not verify_signature("wrong", body, sig)
