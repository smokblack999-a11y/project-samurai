from __future__ import annotations

import json
import os
import time
from app import Message, baseline, analyze
from evaluation import CASES


def score(expected, actual):
    return {
        "intent_ok": actual.intent == expected.expected_intent,
        "action_ok": actual.recommended_action == expected.expected_action,
        "score_ok": actual.lead_score >= expected.min_score,
    }


def run():
    rows = []
    for i, case in enumerate(CASES, 1):
        message = Message(message_id=f"bench-{i}", text=case.text)
        base = baseline(message)
        started = time.perf_counter()
        ai = analyze(message) if os.getenv("OPENAI_API_KEY") else None
        latency_ms = round((time.perf_counter() - started) * 1000, 2) if ai else None
        row = {"id": i, "text": case.text, "baseline": score(case, base), "ai": score(case, ai) if ai else None, "ai_latency_ms": latency_ms}
        rows.append(row)
    out = {"cases": len(rows), "ai_enabled": bool(os.getenv("OPENAI_API_KEY")), "rows": rows}
    if rows:
        out["baseline_intent_accuracy"] = sum(r["baseline"]["intent_ok"] for r in rows) / len(rows)
        out["baseline_action_accuracy"] = sum(r["baseline"]["action_ok"] for r in rows) / len(rows)
        if out["ai_enabled"]:
            out["ai_intent_accuracy"] = sum(r["ai"]["intent_ok"] for r in rows) / len(rows)
            out["ai_action_accuracy"] = sum(r["ai"]["action_ok"] for r in rows) / len(rows)
            out["avg_ai_latency_ms"] = sum(r["ai_latency_ms"] for r in rows) / len(rows)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
