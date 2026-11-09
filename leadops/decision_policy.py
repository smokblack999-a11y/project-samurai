from __future__ import annotations


def policy(lead_score: int, urgency: str) -> str:
    if lead_score >= 70 or urgency == "high":
        return "human_followup"
    return "auto_reply"
