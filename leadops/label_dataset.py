from __future__ import annotations
import json
from pathlib import Path
from redact import redact

INTENTS = {"buying", "information", "support", "spam", "other"}
ACTIONS = {"human_followup", "auto_reply", "ignore", "needs_review"}
OUTCOMES = {"qualified", "not_qualified", "unknown"}


def load(path: str):
    rows = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not row.get("id") or not row.get("text_redacted"):
            raise ValueError(f"line {line_no}: id/text required")
        if row["intent"] not in INTENTS or row["action"] not in ACTIONS or row["outcome"] not in OUTCOMES:
            raise ValueError(f"line {line_no}: invalid label")
        if not 0 <= int(row["score"]) <= 100:
            raise ValueError(f"line {line_no}: score must be 0..100")
        if redact(row["text_redacted"]) != row["text_redacted"]:
            raise ValueError(f"line {line_no}: PII remains in dataset")
        rows.append(row)
    if len(rows) > 10000:
        raise ValueError("dataset exceeds pilot safety limit")
    return rows

if __name__ == "__main__":
    import sys
    print(json.dumps({"rows": len(load(sys.argv[1]))}, ensure_ascii=False))
