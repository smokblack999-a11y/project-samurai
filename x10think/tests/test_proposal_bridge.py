from pydantic import ValidationError

from x10think.openai_agent import Proposal
from x10think.proposal_bridge import bind_proposal


def proposal(action="restart_service"):
    return Proposal(
        summary="backend unhealthy",
        severity="high",
        recommended_action=action,
        rationale="health check failed",
    )


def test_same_material_has_same_fingerprint():
    a = bind_proposal(proposal(), {"service": "backend"})
    b = bind_proposal(proposal(), {"service": "backend"})
    assert a.fingerprint == b.fingerprint


def test_payload_change_changes_fingerprint():
    a = bind_proposal(proposal(), {"service": "backend"})
    b = bind_proposal(proposal(), {"service": "kernel"})
    assert a.fingerprint != b.fingerprint


def test_forbidden_action_cannot_be_bound():
    try:
        p = proposal("execute_shell")
        bind_proposal(p)
    except (ValidationError, ValueError):
        return
    raise AssertionError("forbidden action escaped proposal validation")
