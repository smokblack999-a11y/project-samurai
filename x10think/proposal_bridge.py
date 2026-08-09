from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .openai_agent import Proposal, validate_proposal


@dataclass(frozen=True)
class BoundProposal:
    proposal: Proposal
    fingerprint: str


def canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def bind_proposal(proposal: Proposal, payload: dict[str, Any] | None = None) -> BoundProposal:
    proposal = validate_proposal(proposal)
    payload = payload or {}
    material = {
        "action": proposal.recommended_action,
        "payload": payload,
        "severity": proposal.severity,
        "summary": proposal.summary,
    }
    fingerprint = hashlib.sha256(canonical_payload(material).encode("utf-8")).hexdigest()
    return BoundProposal(proposal=proposal, fingerprint=fingerprint)
