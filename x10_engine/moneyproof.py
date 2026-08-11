from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Signal(str, Enum):
    PAID = "A"
    BUYING_INTENT = "B"
    QUALIFIED_DEMO = "C"
    BUDGET_PAIN = "D"
    WEAK = "E"
    SPECULATION = "F"


class Decision(str, Enum):
    BUILD = "BUILD"
    SELL_TEST = "SELL_TEST"
    RESEARCH = "RESEARCH"
    KILL = "KILL"


@dataclass(frozen=True)
class CommercialEvidence:
    signal: Signal
    source: str
    claim: str
    observed: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence source is required")
        if not self.claim.strip():
            raise ValueError("evidence claim is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class MoneyProof:
    buyer: str
    pain: str
    offer: str
    price_usd: float
    evidence: list[CommercialEvidence] = field(default_factory=list)

    def strongest_signal(self) -> Signal | None:
        if not self.evidence:
            return None
        rank = {Signal.PAID: 6, Signal.BUYING_INTENT: 5, Signal.QUALIFIED_DEMO: 4,
                Signal.BUDGET_PAIN: 3, Signal.WEAK: 2, Signal.SPECULATION: 1}
        return max(self.evidence, key=lambda e: rank[e.signal]).signal

    def decide(self) -> Decision:
        signal = self.strongest_signal()
        if signal in (Signal.PAID, Signal.BUYING_INTENT):
            return Decision.BUILD
        if signal in (Signal.QUALIFIED_DEMO, Signal.BUDGET_PAIN):
            return Decision.SELL_TEST
        if signal is Signal.WEAK:
            return Decision.RESEARCH
        return Decision.KILL

    def score(self) -> float:
        if not self.evidence:
            return 0.0
        rank = {Signal.PAID: 1.0, Signal.BUYING_INTENT: .85, Signal.QUALIFIED_DEMO: .7,
                Signal.BUDGET_PAIN: .55, Signal.WEAK: .25, Signal.SPECULATION: .0}
        weighted = [rank[e.signal] * e.confidence for e in self.evidence]
        return round(max(weighted) * 100, 1)


def decision_from_evidence(evidence: Iterable[CommercialEvidence]) -> Decision:
    items = list(evidence)
    proof = MoneyProof(buyer="", pain="", offer="", price_usd=0, evidence=items)
    return proof.decide()
