from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any


class OperationStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVAL_REQUIRED = "approval_required"
    REJECTED = "rejected"
    EXPIRED = "expired"
    APPROVED = "approved"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    VERIFY_FAILED = "verify_failed"


TERMINAL = {
    OperationStatus.REJECTED,
    OperationStatus.EXPIRED,
    OperationStatus.FAILED,
    OperationStatus.VERIFIED,
    OperationStatus.VERIFY_FAILED,
}


@dataclass
class Operation:
    id: str
    trace_id: str
    action: str
    payload: dict[str, Any]
    risk_score: int
    fingerprint: str
    status: OperationStatus = OperationStatus.PROPOSED
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    execution_id: str | None = None
    error: str | None = None

    @staticmethod
    def make_fingerprint(action: str, payload: dict[str, Any]) -> str:
        canonical = json.dumps(
            {"action": action, "payload": payload},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def is_expired(self, now: float | None = None) -> bool:
        return self.expires_at is not None and (now or time.time()) >= self.expires_at

    def revalidate(self, action: str, payload: dict[str, Any], now: float | None = None) -> bool:
        if self.is_expired(now):
            self.status = OperationStatus.EXPIRED
            return False
        return self.fingerprint == self.make_fingerprint(action, payload)

    def approve(self, ttl_seconds: int = 300) -> None:
        if self.status != OperationStatus.APPROVAL_REQUIRED:
            raise ValueError(f"cannot approve from {self.status}")
        self.expires_at = time.time() + ttl_seconds
        self.status = OperationStatus.APPROVED

    def begin_execution(self, action: str, payload: dict[str, Any]) -> None:
        if self.status != OperationStatus.APPROVED:
            raise ValueError(f"cannot execute from {self.status}")
        if not self.revalidate(action, payload):
            raise ValueError("operation fingerprint mismatch or approval expired")
        self.status = OperationStatus.EXECUTING

    def mark_executed(self, execution_id: str) -> None:
        if self.status != OperationStatus.EXECUTING:
            raise ValueError(f"cannot mark executed from {self.status}")
        self.execution_id = execution_id
        self.status = OperationStatus.EXECUTED

    def start_verification(self) -> None:
        if self.status != OperationStatus.EXECUTED:
            raise ValueError(f"cannot verify from {self.status}")
        self.status = OperationStatus.VERIFYING

    def mark_verified(self, ok: bool) -> None:
        if self.status != OperationStatus.VERIFYING:
            raise ValueError(f"cannot complete verification from {self.status}")
        self.status = OperationStatus.VERIFIED if ok else OperationStatus.VERIFY_FAILED

    def mark_failed(self, error: str) -> None:
        self.error = error
        self.status = OperationStatus.FAILED
