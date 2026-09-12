from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Literal
import hashlib
import json

Decision = Literal["ALLOW", "REVIEW", "BLOCK"]
Permission = Literal["READ", "DRAFT", "APPROVAL", "AUTONOMOUS"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Evidence:
    source: str
    fact: str
    observed_at: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class ActionEnvelope:
    agent_id: str
    agent_version: str
    tool: str
    target: str
    intent: str
    permission: Permission
    evidence: list[Evidence] = field(default_factory=list)
    risk_score: float = 0.0
    estimated_cost_usd: float = 0.0
    reversible: bool = True
    blast_radius: int = 1
    action_id: str = field(default_factory=lambda: hashlib.sha256(utc_now().encode()).hexdigest()[:20])
    created_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.agent_id or not self.tool or not self.target:
            raise ValueError("agent_id, tool and target are required")
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError("risk_score must be between 0 and 1")
        if self.estimated_cost_usd < 0:
            raise ValueError("estimated_cost_usd cannot be negative")
        if self.blast_radius < 1:
            raise ValueError("blast_radius must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionRecord:
    action_id: str
    decision: Decision
    reason: str
    policy_rule: str
    decided_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
