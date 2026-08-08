from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionClass(str, Enum):
    READ = "read"
    SAFE_WRITE = "safe_write"
    SENSITIVE = "sensitive"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    classification: ActionClass
    allowed: bool
    requires_approval: bool
    reason: str


POLICIES: dict[str, ActionClass] = {
    "health": ActionClass.READ,
    "disk_report": ActionClass.READ,
    "write_report": ActionClass.SAFE_WRITE,
    "restart_service": ActionClass.SENSITIVE,
    "execute_shell": ActionClass.FORBIDDEN,
    "delete_files": ActionClass.FORBIDDEN,
}


def evaluate(action: str) -> PolicyDecision:
    classification = POLICIES.get(action, ActionClass.FORBIDDEN)
    if classification is ActionClass.READ:
        return PolicyDecision(action, classification, True, False, "Read-only telemetry action")
    if classification is ActionClass.SAFE_WRITE:
        return PolicyDecision(action, classification, True, True, "Reversible write requires operator approval")
    if classification is ActionClass.SENSITIVE:
        return PolicyDecision(action, classification, True, True, "Sensitive operation requires explicit approval")
    return PolicyDecision(action, classification, False, True, "Action is forbidden by default")
