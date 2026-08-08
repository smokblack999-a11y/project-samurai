from policy import ActionClass, evaluate


def test_read_is_immediate():
    d = evaluate("health")
    assert d.classification is ActionClass.READ
    assert d.allowed is True
    assert d.requires_approval is False


def test_sensitive_requires_approval():
    d = evaluate("restart_service")
    assert d.classification is ActionClass.SENSITIVE
    assert d.allowed is True
    assert d.requires_approval is True


def test_unknown_is_forbidden():
    d = evaluate("rm_everything")
    assert d.classification is ActionClass.FORBIDDEN
    assert d.allowed is False
