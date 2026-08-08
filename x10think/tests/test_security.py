from policy import ActionClass, evaluate
from security import approval_fingerprint, constant_time_equal


def test_fingerprint_is_stable_and_payload_bound():
    a = approval_fingerprint("health", {"scope": "local"})
    b = approval_fingerprint("health", {"scope": "local"})
    c = approval_fingerprint("health", {"scope": "other"})
    assert a == b
    assert a != c


def test_shell_is_forbidden():
    assert evaluate("execute_shell").classification is ActionClass.FORBIDDEN
    assert evaluate("execute_shell").allowed is False


def test_constant_time_compare():
    assert constant_time_equal("abc", "abc")
    assert not constant_time_equal("abc", "abd")
