from __future__ import annotations


def gate(metrics: dict, paid_pilots: int = 0) -> dict:
    precision = float(metrics.get('precision', 0))
    recall = float(metrics.get('recall', 0))
    f1 = float(metrics.get('f1', 0))
    return {
        'quality_pass': precision >= 0.80 and recall >= 0.70 and f1 >= 0.75,
        'paid_pilot_pass': paid_pilots >= 1,
        'scale_pass': precision >= 0.90 and recall >= 0.80 and paid_pilots >= 3,
    }
