from core import health, safe_action


def test_health_shape():
    result = health()
    assert 0 <= result["score"] <= 100
    assert "snapshot" in result
    assert "findings" in result


def test_action_allowlist():
    assert safe_action("health")["ok"] is True
    assert safe_action("rm -rf /")["ok"] is False
