from metrics import classification_metrics


def test_metrics():
    result = classification_metrics(
        ["buying", "buying", "information", "information"],
        ["buying", "information", "buying", "information"],
        "buying",
    )
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5
    assert result["false_positive_rate"] == 0.5
