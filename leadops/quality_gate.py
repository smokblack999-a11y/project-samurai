from __future__ import annotations


def quality_gate(metrics: dict, real_messages: int, paid_pilots: int) -> dict:
    precision = metrics.get("precision", 0.0)
    recall = metrics.get("recall", 0.0)
    f1 = metrics.get("f1", 0.0)
    ready = (
        real_messages >= 100
        and paid_pilots >= 1
        and precision >= 0.90
        and recall >= 0.85
        and f1 >= 0.87
    )
    return {
        "pilot_ready": ready,
        "real_messages": real_messages,
        "paid_pilots": paid_pilots,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "reason": "all evidence thresholds passed" if ready else "real pilot evidence is insufficient",
    }
