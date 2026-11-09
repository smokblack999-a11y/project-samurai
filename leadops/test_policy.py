from decision_policy import policy


def test_hot_lead_goes_to_human():
    assert policy(90, "low") == "human_followup"


def test_high_urgency_goes_to_human():
    assert policy(20, "high") == "human_followup"


def test_low_signal_can_auto_reply():
    assert policy(20, "low") == "auto_reply"
