from ai import _parse_json, _provider


def test_provider_prefers_explicit_setting(monkeypatch):
    monkeypatch.setenv("X10_AI_PROVIDER", "openai")
    monkeypatch.setenv("TOGETHER_API_KEY", "test")
    assert _provider() == "openai"


def test_auto_uses_together_when_available(monkeypatch):
    monkeypatch.delenv("X10_AI_PROVIDER", raising=False)
    monkeypatch.setenv("TOGETHER_API_KEY", "test")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert _provider() == "together"


def test_parse_json_requires_contract():
    result = _parse_json({"summary": "ok", "severity": "low", "findings": [], "next_steps": []}.__repr__().replace("'", '"'))
    assert result["severity"] == "low"


def test_parse_json_rejects_non_object():
    try:
        _parse_json("[]")
    except ValueError:
        return
    raise AssertionError("expected ValueError")
