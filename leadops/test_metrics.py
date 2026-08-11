from metrics import classification_metrics, operational_summary


def test_metrics_for_buying():
    result = classification_metrics(["buying", "information", "buying"], ["buying", "buying", "information"], "buying")
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_operational_summary():
    result = operational_summary([
        {"intent": "buying", "recommended_action": "human_followup", "urgency": "high"},
        {"intent": "information", "recommended_action": "auto_reply", "urgency": "low"},
    ])
    assert result == {
        "processed": 2,
        "buying": 1,
        "information": 1,
        "human_followup": 1,
        "auto_reply": 1,
        "high_urgency": 1,
    }
