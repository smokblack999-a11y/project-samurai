from __future__ import annotations

import json

from x10think.together import TogetherConfig, TogetherError, diagnose


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({"choices": [{"message": {"content": "safe next step"}}]}).encode()


def test_missing_key_is_explicit(monkeypatch):
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    assert TogetherConfig.from_env() is None
    try:
        diagnose("check disk")
    except TogetherError as exc:
        assert "TOGETHER_API_KEY" in str(exc)
    else:
        raise AssertionError("expected missing-key error")


def test_diagnose_uses_config(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode())
        return FakeResponse()

    monkeypatch.setattr("x10think.together.urlopen", fake_urlopen)
    cfg = TogetherConfig(api_key="test-key", model="openai/gpt-oss-20b")
    assert diagnose("check memory", config=cfg) == "safe next step"
    assert captured["url"] == "https://api.together.ai/v1/chat/completions"
    assert captured["body"]["model"] == "openai/gpt-oss-20b"
    assert captured["body"]["messages"][-1]["content"] == "check memory"
