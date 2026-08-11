from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OpportunityStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    TEST = "TEST"
    PROVEN = "PROVEN"
    KILLED = "KILLED"


@dataclass
class Assumption:
    claim: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    test: str = ""
    result: str = ""
    status: str = "OPEN"

    def update(self, result: str, confidence: float, status: str) -> None:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        self.result = result
        self.confidence = confidence
        self.status = status


@dataclass
class Opportunity:
    problem: str
    buyer: str
    trigger: str
    offer: str
    pain: float
    urgency: float
    willingness_to_pay: float
    competition: float
    customer_access: float
    build_cost: float
    time_to_money: float
    assumptions: list[Assumption] = field(default_factory=list)
    status: OpportunityStatus = OpportunityStatus.UNVERIFIED

    def score(self) -> float:
        positives = (
            self.pain * self.urgency * self.willingness_to_pay * self.customer_access
        )
        friction = max(1.0, self.competition + self.build_cost + self.time_to_money)
        evidence = sum(a.confidence for a in self.assumptions) / max(1, len(self.assumptions))
        return round((positives / friction) * evidence, 2)

    def kill_conditions(self) -> list[str]:
        reasons: list[str] = []
        if self.competition > 70:
            reasons.append("competition_above_threshold")
        if self.customer_access < 50:
            reasons.append("buyer_hard_to_reach")
        if self.pain < 60:
            reasons.append("pain_below_threshold")
        if self.time_to_money > 90:
            reasons.append("time_to_money_too_high")
        if not self.assumptions:
            reasons.append("no_evidence")
        return reasons
