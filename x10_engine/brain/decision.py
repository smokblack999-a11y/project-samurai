from dataclasses import dataclass
from typing import Literal

Decision = Literal["GO", "REWORK", "KILL"]


@dataclass(frozen=True)
class Opportunity:
    pain: float
    money: float
    speed: float
    access: float
    uniqueness: float
    competition: float
    evidence: float
    exitability: float

    def normalized(self) -> dict[str, float]:
        return {k: max(0.0, min(100.0, float(v))) for k, v in self.__dict__.items()}


def evaluate(o: Opportunity) -> dict:
    s = o.normalized()
    # Weighted for speed-to-proof and commercial access, not vanity market size.
    score = (
        0.18 * s["pain"] +
        0.18 * s["money"] +
        0.16 * s["speed"] +
        0.16 * s["access"] +
        0.10 * s["uniqueness"] +
        0.10 * (100 - s["competition"]) +
        0.08 * s["evidence"] +
        0.04 * s["exitability"]
    )

    hard_fail = []
    if s["evidence"] < 35:
        hard_fail.append("insufficient evidence")
    if s["pain"] < 45:
        hard_fail.append("weak pain")
    if s["access"] < 35:
        hard_fail.append("weak buyer access")

    if hard_fail or score < 45:
        decision: Decision = "KILL"
    elif score < 68 or s["competition"] > 70:
        decision = "REWORK"
    else:
        decision = "GO"

    return {
        "score": round(score, 2),
        "decision": decision,
        "hard_fail": hard_fail,
        "next_move": {
            "GO": "build the cheapest proof and seek a paid pilot",
            "REWORK": "change wedge, offer, channel, or proof strategy",
            "KILL": "stop investment and record the lesson",
        }[decision],
    }
