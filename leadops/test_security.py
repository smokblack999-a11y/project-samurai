from auth import valid_api_key
from privacy import fingerprint_message, redact_for_export


def test_api_key_compare():
    assert valid_api_key("abc", "abc")
    assert not valid_api_key("abc", "abd")
    assert not valid_api_key(None, "abc")


def test_fingerprint_is_stable_without_logging_plaintext():
    assert fingerprint_message("hello") == fingerprint_message("hello")
    assert fingerprint_message("hello") != fingerprint_message("hello2")


def test_redaction_bounds_export_size():
    value = redact_for_export("x" * 300, limit=20)
    assert len(value) <= 21
