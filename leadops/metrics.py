from __future__ import annotations


def rate(values: list[bool]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def classification_metrics(expected: list[str], actual: list[str], positive: str) -> dict[str, float]:
    tp = sum(e == positive and a == positive for e, a in zip(expected, actual))
    fp = sum(e != positive and a == positive for e, a in zip(expected, actual))
    fn = sum(e == positive and a != positive for e, a in zip(expected, actual))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
