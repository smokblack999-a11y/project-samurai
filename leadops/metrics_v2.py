from __future__ import annotations

def binary_metrics(rows):
    tp = sum(bool(r['predicted']) and bool(r['actual']) for r in rows)
    fp = sum(bool(r['predicted']) and not bool(r['actual']) for r in rows)
    fn = sum(not bool(r['predicted']) and bool(r['actual']) for r in rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': precision, 'recall': recall, 'f1': f1}
