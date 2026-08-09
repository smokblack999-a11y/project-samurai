import pytest

from openai_agent import Proposal


def test_proposal_rejects_extra_fields():
    with pytest.raises(Exception):
        Proposal(
            summary="ok",
            severity="low",
            recommended_action="health",
            rationale="safe",
            execute="rm -rf /",
        )


def test_proposal_action_is_allowlisted():
    with pytest.raises(Exception):
        Proposal(
            summary="bad",
            severity="high",
            recommended_action="execute_shell",
            rationale="unsafe",
        )
