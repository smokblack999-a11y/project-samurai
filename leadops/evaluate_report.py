from __future__ import annotations

import json
from pathlib import Path
from evaluation import run
from roi import calculate, BusinessInput


def build_report() -> dict:
    evaluation = run()
    roi = calculate(BusinessInput(5000, 100, 0.10, 200, 149))
    synthetic_ok = evaluation["intent_accuracy"] >= 0.90 and evaluation["action_accuracy"] >= 0.90
    return {
        "product": "Telegram LeadOps AI",
        "evaluation": evaluation,
        "business_model": roi,
        "gates": {
            "synthetic_pilot_ready": synthetic_ok,
            "sales_ready": False,
            "reason": "real labeled pilot data and a paid pilot are required before sales_ready can become true",
        },
        "next_gate": {
            "minimum_real_messages": 100,
            "minimum_paid_pilots": 1,
            "required_metrics": ["precision", "recall", "f1", "false_positive_rate", "latency", "cost_per_message"],
        },
        "warning": "Synthetic baseline cases are not evidence of market demand or production accuracy.",
    }

if __name__ == "__main__":
    report = build_report()
    out = Path("reports/latest_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
