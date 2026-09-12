import tempfile
from pathlib import Path

from control_plane.ledger import AuditLedger
from control_plane.models import ActionEnvelope, Evidence
from control_plane.policy import PolicyEngine
from control_plane.trust import TrustEngine


def action(**overrides):
    base = dict(
        agent_id="github-fixer",
        agent_version="0.1.0",
        tool="run_tests",
        target="repo/main",
        intent="verify patch",
        permission="AUTONOMOUS",
        evidence=[Evidence("ci", "tests passed", "2026-09-12T00:00:00+00:00")],
        risk_score=0.05,
        estimated_cost_usd=0.20,
        reversible=True,
        blast_radius=1,
    )
    base.update(overrides)
    return ActionEnvelope(**base)


def test_safe_autonomous_action_is_allowed():
    decision = PolicyEngine().evaluate(action())
    assert decision.decision == "ALLOW"


def test_high_risk_action_requires_review():
    decision = PolicyEngine().evaluate(action(risk_score=0.40))
    assert decision.decision == "REVIEW"


def test_dangerous_tool_is_blocked_even_with_low_risk():
    decision = PolicyEngine().evaluate(action(tool="delete_database", risk_score=0.0))
    assert decision.decision == "BLOCK"


def test_mutation_without_evidence_is_blocked():
    decision = PolicyEngine().evaluate(action(permission="APPROVAL", evidence=[]))
    assert decision.decision == "BLOCK"


def test_trust_changes_with_outcomes():
    trust = TrustEngine()
    before = trust.score("agent-x")
    after = trust.record("agent-x", success=True, evidence_quality=1.0)
    assert after > before
    after_failure = trust.record("agent-x", success=False, rollback=True, evidence_quality=0.0)
    assert after_failure < after


def test_ledger_round_trip():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "audit.jsonl"
        ledger = AuditLedger(str(path))
        current = action()
        decision = PolicyEngine().evaluate(current)
        ledger.append(current, decision, {"status": "verified"})
        events = ledger.read_all()
        assert len(events) == 1
        assert events[0]["decision"]["decision"] == "ALLOW"
