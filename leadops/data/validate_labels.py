from __future__ import annotations
import json
import sys

ALLOWED_INTENTS={"buying","information","support","spam_other"}
ALLOWED_URGENCY={"low","high"}
ALLOWED_ACTIONS={"human_followup","auto_reply","ignore"}


def validate(path: str) -> int:
    rows=[]
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip(): continue
            row=json.loads(line)
            required={"id","text","intent","lead_score","urgency","action"}
            missing=required-set(row)
            if missing: raise ValueError(f"line {line_no}: missing {sorted(missing)}")
            if row["intent"] not in ALLOWED_INTENTS: raise ValueError(f"line {line_no}: invalid intent")
            if row["urgency"] not in ALLOWED_URGENCY: raise ValueError(f"line {line_no}: invalid urgency")
            if row["action"] not in ALLOWED_ACTIONS: raise ValueError(f"line {line_no}: invalid action")
            if not 0 <= int(row["lead_score"]) <= 100: raise ValueError(f"line {line_no}: score out of range")
            if not row["text"].strip(): raise ValueError(f"line {line_no}: empty text")
            rows.append(row)
    print(json.dumps({"valid":True,"rows":len(rows)},ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(validate(sys.argv[1]))
