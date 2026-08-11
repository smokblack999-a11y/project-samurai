from __future__ import annotations

from collections import Counter


def rate(values: list[bool]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def classification_metrics(expected: list[str], actual: list[str], positive: str) -> dict[str, float]:
    if len(expected) != len(actual) or not expected:
        raise ValueError("expected and actual must have equal non-zero length")
    tp = sum(e == positive and a == positive for e, a in zip(expected, actual))
    fp = sum(e != positive and a == positive for e, a in zip(expected, actual))
    fn = sum(e == positive and a != positive for e, a in zip(expected, actual))
    tn = sum(e != positive and a != positive for e, a in zip(expected, actual))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4), "false_positive_rate": round(fpr, 4)}


def operational_summary(decisions: list[dict]) -> dict[str, int]:
    intents = Counter(d.get("intent") for d in decisions)
    actions = Counter(d.get("recommended_action") for d in decisions)
    urgency = Counter(d.get("urgency") for d in decisions)
    return {"processed": len(decisions), "buying": intents["buying"], "information": intents["information"], "human_followup": actions["human_followup"], "auto_reply": actions["auto_reply"], "high_urgency": urgency["high"]}
