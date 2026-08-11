from __future__ import annotations

import json
from pathlib import Path
from evaluation import run
from roi import calculate, BusinessInput


def build_report() -> dict:
    evaluation = run()
    roi = calculate(BusinessInput(5000, 100, 0.10, 200, 149))
    return {
        "product": "Telegram LeadOps AI",
        "evaluation": evaluation,
        "business_model": roi,
        "gates": {
            "pilot_ready": evaluation["intent_accuracy"] >= 0.90 and evaluation["action_accuracy"] >= 0.90,
            "sales_ready": evaluation["intent_accuracy"] >= 0.90 and roi["roi_multiplier"] >= 5,
        },
        "warning": "Synthetic baseline cases are not evidence of market demand; replace them with labeled pilot data before claiming production accuracy or ROI.",
    }

if __name__ == "__main__":
    report = build_report()
    out = Path("reports/latest_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
