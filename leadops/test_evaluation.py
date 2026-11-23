from evaluation import run

def test_baseline_evaluation():
    result = run()
    assert result["cases"] >= 8
    assert result["intent_accuracy"] >= 0.90
    assert result["action_accuracy"] >= 0.90
    assert result["score_threshold_rate"] >= 0.90
