from __future__ import annotations


def gate(metrics: dict) -> dict:
    precision = metrics.get('precision', 0.0)
    recall = metrics.get('recall', 0.0)
    f1 = metrics.get('f1', 0.0)
    return {'pilot_quality_gate': precision >= 0.80 and recall >= 0.70 and f1 >= 0.75}
