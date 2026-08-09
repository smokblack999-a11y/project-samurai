from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    workflow: str = "x10think-sentinel-analysis"

    @classmethod
    def new(cls) -> "TraceContext":
        return cls(trace_id=uuid.uuid4().hex)

    def audit_fields(self) -> dict[str, str]:
        return {"trace_id": self.trace_id, "workflow": self.workflow}
