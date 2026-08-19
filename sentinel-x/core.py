from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4


@dataclass
class Event:
    source: str
    kind: str
    host: str
    timestamp: str
    severity: int = 0
    confidence: float = 0.5
    process: str | None = None
    parent_process: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    remote_ip: str | None = None
    user: str | None = None
    tags: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        allowed = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        allowed.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        allowed.setdefault("source", "unknown")
        allowed.setdefault("kind", "unknown")
        allowed.setdefault("host", "unknown")
        allowed["raw"] = data
        return cls(**allowed)


@dataclass
class Incident:
    id: str
    host: str
    score: int
    confidence: float
    created_at: str
    updated_at: str
    evidence: list[Event] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "host": self.host,
            "score": self.score,
            "confidence": round(self.confidence, 3),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reasons": self.reasons,
            "evidence_count": len(self.evidence),
            "evidence": [e.raw for e in self.evidence],
        }


class RiskEngine:
    """Deterministic, explainable first-pass scoring. No ML dependency."""

    WEIGHTS = {
        "process_exec": 12,
        "privileged_exec": 22,
        "network_connect": 8,
        "file_modify": 10,
        "persistence": 28,
        "yara_match": 35,
        "credential_access": 30,
        "container_escape": 40,
    }

    def score(self, events: list[Event]) -> tuple[int, float, list[str]]:
        score = 0
        reasons: list[str] = []
        confidence = 0.0
        for event in events:
            base = self.WEIGHTS.get(event.kind, max(0, event.severity))
            score += int(base * max(0.0, min(1.0, event.confidence)))
            confidence = max(confidence, event.confidence)
            if base >= 20:
                reasons.append(f"{event.source}:{event.kind} (+{base})")

        # Correlation bonuses reduce false positives from isolated events.
        kinds = {e.kind for e in events}
        if {"process_exec", "network_connect"} <= kinds:
            score += 10
            reasons.append("process-to-network correlation (+10)")
        if {"file_modify", "persistence"} <= kinds:
            score += 15
            reasons.append("file-to-persistence correlation (+15)")
        if {"yara_match", "process_exec"} <= kinds:
            score += 20
            reasons.append("malware-indicator-to-execution correlation (+20)")

        return min(score, 100), confidence, reasons


class IncidentStore:
    def __init__(self) -> None:
        self.incidents: dict[str, Incident] = {}
        self.engine = RiskEngine()

    def ingest(self, event: Event) -> Incident:
        related = [e for i in self.incidents.values() if i.host == event.host for e in i.evidence]
        evidence = (related + [event])[-100:]
        score, confidence, reasons = self.engine.score(evidence)
        now = datetime.now(timezone.utc).isoformat()
        incident_id = self._incident_id(event.host, evidence)
        incident = Incident(incident_id, event.host, score, confidence, now, now, evidence, reasons)
        self.incidents[incident_id] = incident
        return incident

    def _incident_id(self, host: str, evidence: list[Event]) -> str:
        material = host + "|" + "|".join(f"{e.timestamp}:{e.kind}:{e.process}:{e.file_hash}" for e in evidence[-10:])
        return sha256(material.encode()).hexdigest()[:16]

    def list(self) -> list[Incident]:
        return sorted(self.incidents.values(), key=lambda x: x.updated_at, reverse=True)

    def get(self, incident_id: str) -> Incident | None:
        return self.incidents.get(incident_id)
