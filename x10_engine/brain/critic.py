from dataclasses import dataclass


@dataclass(frozen=True)
class Critique:
    reasons: list[str]
    kill_score: float
    mandatory_tests: list[str]


def attack(opportunity: dict) -> Critique:
    reasons: list[str] = []
    tests: list[str] = []

    competition = float(opportunity.get("competition", 100))
    access = float(opportunity.get("access", opportunity.get("customer_access", 0)))
    pain = float(opportunity.get("pain", 0))
    evidence = float(opportunity.get("evidence", 0))
    speed = float(opportunity.get("speed", opportunity.get("time_to_money", 0)))
    money = float(opportunity.get("money", 0))

    if competition > 70:
        reasons.append("competition is high")
        tests.append("identify a narrower underserved wedge")
    if access < 35:
        reasons.append("buyer access is weak")
        tests.append("produce five real buyer paths")
    if pain < 45:
        reasons.append("pain may be non-urgent")
        tests.append("obtain explicit problem evidence from buyers")
    if evidence < 35:
        reasons.append("evidence is weak")
        tests.append("run the cheapest falsification experiment")
    if speed > 90:
        reasons.append("time-to-money is too long")
        tests.append("design a fixed-scope paid pilot")
    if money < 45:
        reasons.append("willingness-to-pay is uncertain")
        tests.append("test a concrete paid offer")

    kill_score = min(100.0, len(reasons) * 16.0)
    return Critique(reasons, kill_score, tests)
