from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrustState:
    success: int = 0
    failure: int = 0
    rollback: int = 0
    security_incident: int = 0
    evidence_quality_sum: float = 0.0
    evidence_events: int = 0

    def score(self) -> float:
        total = self.success + self.failure + self.rollback + self.security_incident
        if total == 0:
            return 50.0
        reliability = self.success / total
        penalty = min(0.45, self.rollback * 0.05 + self.security_incident * 0.15)
        evidence = self.evidence_quality_sum / self.evidence_events if self.evidence_events else 0.5
        return round(max(0.0, min(100.0, 100 * (0.70 * reliability + 0.30 * evidence - penalty))), 2)


class TrustEngine:
    def __init__(self) -> None:
        self._states: dict[str, TrustState] = {}

    def state(self, agent_id: str) -> TrustState:
        return self._states.setdefault(agent_id, TrustState())

    def record(self, agent_id: str, *, success: bool, rollback: bool = False, security_incident: bool = False, evidence_quality: float = 0.0) -> float:
        if not 0.0 <= evidence_quality <= 1.0:
            raise ValueError("evidence_quality must be between 0 and 1")
        state = self.state(agent_id)
        if success:
            state.success += 1
        else:
            state.failure += 1
        if rollback:
            state.rollback += 1
        if security_incident:
            state.security_incident += 1
        state.evidence_quality_sum += evidence_quality
        state.evidence_events += 1
        return state.score()

    def score(self, agent_id: str) -> float:
        return self.state(agent_id).score()
