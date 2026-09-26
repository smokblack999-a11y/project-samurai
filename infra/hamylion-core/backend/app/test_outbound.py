from .outbound import OutboundPolicyError, validate_url


def test_outbound_requires_allowlist(monkeypatch):
    monkeypatch.setattr("app.outbound.settings.OUTBOUND_ALLOWED_HOSTS", {"api.example.com"})
    assert validate_url("https://api.example.com/data") == "https://api.example.com/data"


def test_outbound_rejects_private_destination(monkeypatch):
    monkeypatch.setattr("app.outbound.settings.OUTBOUND_ALLOWED_HOSTS", {"localhost"})
    try:
        validate_url("http://localhost:8080/data")
    except OutboundPolicyError:
        pass
    else:
        raise AssertionError("private destination must be rejected")
