from benchmark_report import gate
from metrics import classification_metrics


def test_metrics_perfect_classifier():
    result = classification_metrics(['buying','information'], ['buying','information'], 'buying')
    assert result['precision'] == 1.0
    assert result['recall'] == 1.0
    assert result['f1'] == 1.0


def test_gate_rejects_weak_recall():
    assert gate({'precision': 0.95, 'recall': 0.2, 'f1': 0.3})['pilot_quality_gate'] is False
