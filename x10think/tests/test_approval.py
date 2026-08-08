from approval import create, decide, get


def test_approval_lifecycle():
    item = create("health", {"reason": "scheduled"})
    assert item["status"] == "pending"

    approved = decide(item["id"], "approve", "operator reviewed")
    assert approved["status"] == "approved"
    assert get(item["id"])["comment"] == "operator reviewed"


def test_disallowed_action_rejected():
    try:
        create("shell_exec", {"command": "rm -rf /"})
    except ValueError as exc:
        assert str(exc) == "action_not_allowlisted"
    else:
        raise AssertionError("unsafe action was accepted")
