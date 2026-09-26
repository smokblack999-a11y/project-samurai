from .outbound import OutboundPolicyError, validate_url


def test_outbound_requires_allowlist(monkeypatch):
    monkeypatch.setattr("app.outbound.settings.OUTBOUND_ALLOWED_HOSTS", {"api.example.com"})
    monkeypatch.setattr(
        "app.outbound.socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )
    assert validate_url("https://api.example.com/data") == "https://api.example.com/data"


def test_outbound_rejects_private_destination(monkeypatch):
    monkeypatch.setattr("app.outbound.settings.OUTBOUND_ALLOWED_HOSTS", {"localhost"})
    monkeypatch.setattr(
        "app.outbound.socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("127.0.0.1", 8080))],
    )
    try:
        validate_url("http://localhost:8080/data")
    except OutboundPolicyError:
        pass
    else:
        raise AssertionError("private destination must be rejected")
