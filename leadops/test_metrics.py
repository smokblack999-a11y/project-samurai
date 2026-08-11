from metrics import classification_metrics


def test_metrics_for_buying():
    result = classification_metrics(["buying", "information", "buying"], ["buying", "buying", "information"], "buying")
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5
