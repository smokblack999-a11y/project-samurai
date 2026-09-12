from __future__ import annotations

from dataclasses import dataclass

from .models import ActionEnvelope, Decision, DecisionRecord, utc_now


@dataclass(frozen=True)
class Policy:
    max_autonomous_risk: float = 0.20
    max_autonomous_blast_radius: int = 2
    max_autonomous_cost_usd: float = 2.00
    require_evidence_for_mutations: bool = True
    blocked_tools: frozenset[str] = frozenset({"delete_database", "rotate_root_credentials"})


class PolicyEngine:
    """Deterministic first-pass gate. No LLM is allowed to override a block."""

    def __init__(self, policy: Policy | None = None) -> None:
        self.policy = policy or Policy()

    def evaluate(self, action: ActionEnvelope) -> DecisionRecord:
        p = self.policy

        if action.tool in p.blocked_tools:
            return DecisionRecord(action.action_id, "BLOCK", "tool is explicitly blocked", "BLOCKED_TOOL")

        mutation = action.permission in {"APPROVAL", "AUTONOMOUS"} or not action.reversible
        if mutation and p.require_evidence_for_mutations and not action.evidence:
            return DecisionRecord(action.action_id, "BLOCK", "mutation has no evidence", "EVIDENCE_REQUIRED")

        if action.risk_score > 0.80 or action.blast_radius > 10:
            return DecisionRecord(action.action_id, "BLOCK", "risk or blast radius exceeds hard limit", "HARD_RISK_LIMIT")

        if action.permission == "READ":
            return DecisionRecord(action.action_id, "ALLOW", "read-only action", "READ_ALLOW")

        if action.permission == "DRAFT":
            return DecisionRecord(action.action_id, "ALLOW", "draft action has no irreversible execution", "DRAFT_ALLOW")

        if action.permission == "AUTONOMOUS":
            if action.risk_score <= p.max_autonomous_risk and action.blast_radius <= p.max_autonomous_blast_radius and action.estimated_cost_usd <= p.max_autonomous_cost_usd and action.reversible:
                return DecisionRecord(action.action_id, "ALLOW", "within autonomous policy envelope", "AUTONOMOUS_ALLOW")
            return DecisionRecord(action.action_id, "REVIEW", "outside autonomous envelope; human approval required", "AUTONOMOUS_REVIEW")

        if action.permission == "APPROVAL":
            return DecisionRecord(action.action_id, "REVIEW", "explicit approval required", "APPROVAL_REQUIRED")

        return DecisionRecord(action.action_id, "BLOCK", "unknown permission level", "UNKNOWN_PERMISSION")
