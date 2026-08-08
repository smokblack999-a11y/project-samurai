import json

import ai


def test_large_payload_is_rejected():
    result = ai.analyze({"log": "x" * (ai.MAX_INPUT_CHARS + 1)})
    assert result["enabled"] is False
    assert result["reason"] == "payload_too_large"


def test_non_object_payload_is_rejected():
    result = ai.analyze([])
    assert result["enabled"] is False
    assert result["reason"] == "payload_must_be_object"
