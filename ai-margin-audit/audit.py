#!/usr/bin/env python3
"""Deterministic AI spend audit. No synthetic savings claims."""

import csv
import sys
from collections import defaultdict

REQUIRED = ["timestamp", "provider", "model", "input_tokens", "output_tokens", "cost_usd"]


def num(value):
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def audit(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        for r in reader:
            r["cost_usd_num"] = num(r["cost_usd"])
            rows.append(r)

    total = sum(r["cost_usd_num"] for r in rows)
    groups = {}
    for key in ("provider", "model", "feature", "customer"):
        bucket = defaultdict(float)
        for r in rows:
            label = (r.get(key) or "UNATTRIBUTED").strip() or "UNATTRIBUTED"
            bucket[label] += r["cost_usd_num"]
        groups[key] = sorted(bucket.items(), key=lambda x: x[1], reverse=True)

    print("AI MARGIN AUDIT")
    print("===============")
    print(f"Rows: {len(rows)}")
    print(f"Measured spend: ${total:,.2f}")
    print()

    for key, items in groups.items():
        print(key.upper())
        for label, value in items[:10]:
            pct = (value / total * 100) if total else 0
            print(f"  {label}: ${value:,.2f} ({pct:.1f}%)")
        print()

    missing_feature = sum(1 for r in rows if not (r.get("feature") or "").strip())
    missing_customer = sum(1 for r in rows if not (r.get("customer") or "").strip())
    print("CONTROL GAPS")
    print(f"  Rows without feature attribution: {missing_feature}/{len(rows)}")
    print(f"  Rows without customer attribution: {missing_customer}/{len(rows)}")

    if total == 0:
        print("  No measured spend found; optimization conclusions are unavailable.")
    else:
        top_model, top_cost = groups["model"][0]
        print(f"  Largest measured model bucket: {top_model} at ${top_cost:,.2f}")
        print("  Next action: inspect the highest-cost model/workflow before changing providers.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audit.py usage.csv")
        raise SystemExit(2)
    audit(sys.argv[1])
