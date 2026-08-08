from policy import ActionClass, evaluate
from rbac import can


def test_read_pipeline_needs_no_approval():
    decision = evaluate("health")
    assert decision.classification is ActionClass.READ
    assert decision.allowed
    assert not decision.requires_approval


def test_sensitive_pipeline_requires_operator_approval():
    decision = evaluate("restart_service")
    assert decision.classification is ActionClass.SENSITIVE
    assert decision.allowed
    assert decision.requires_approval
    assert can("operator", "approve")
    assert not can("viewer", "approve")


def test_forbidden_pipeline_stops_before_approval():
    decision = evaluate("execute_shell")
    assert decision.classification is ActionClass.FORBIDDEN
    assert not decision.allowed


def test_unknown_actions_fail_closed():
    decision = evaluate("anything_not_registered")
    assert not decision.allowed
    assert decision.classification is ActionClass.FORBIDDEN
