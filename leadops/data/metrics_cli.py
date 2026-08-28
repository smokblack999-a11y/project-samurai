from __future__ import annotations
import json
import sys
from metrics import binary_metrics

if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: metrics_cli.py TP FP FN')
    tp, fp, fn = map(int, sys.argv[1:])
    print(json.dumps(binary_metrics(tp, fp, fn), indent=2))
