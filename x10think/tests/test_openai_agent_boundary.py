import pytest

from x10think.openai_agent import ALLOWED_ACTIONS, validate_proposal


def test_allowed_actions_have_no_shell_capability():
    assert "execute_shell" not in ALLOWED_ACTIONS
    assert "rm_rf" not in ALLOWED_ACTIONS
    assert "write_file" not in ALLOWED_ACTIONS


def test_invalid_action_is_rejected():
    class FakeProposal:
        recommended_action = "execute_shell"

    with pytest.raises(ValueError, match="proposal_action_not_allowed"):
        validate_proposal(FakeProposal())
