from dataclasses import dataclass, field


@dataclass
class Hypothesis:
    target: str
    buyer: str
    problem: str
    offer: str
    success_criterion: str
    falsifier: str
    evidence: list[dict] = field(default_factory=list)
    status: str = "UNTESTED"

    def falsification_plan(self) -> dict:
        return {
            "target": self.target,
            "buyer": self.buyer,
            "claim": self.problem,
            "test": self.success_criterion,
            "kill_condition": self.falsifier,
            "minimum_evidence": 1,
        }

    def add_evidence(self, source: str, claim: str, confidence: float) -> None:
        self.evidence.append({
            "source": source,
            "claim": claim,
            "confidence": max(0.0, min(1.0, confidence)),
        })

    def classify(self) -> str:
        if not self.evidence:
            self.status = "UNTESTED"
            return self.status
        confidence = sum(x["confidence"] for x in self.evidence) / len(self.evidence)
        self.status = "SUPPORTED" if confidence >= 0.75 else "REWORK"
        return self.status
