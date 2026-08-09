from __future__ import annotations

from threading import Lock
from typing import Optional

from .operation import Operation, OperationStatus


class OperationStore:
    """In-memory MVP store with replay protection for operation execution."""

    def __init__(self) -> None:
        self._items: dict[str, Operation] = {}
        self._executions: dict[str, str] = {}
        self._lock = Lock()

    def put(self, operation: Operation) -> Operation:
        with self._lock:
            if operation.id in self._items:
                raise ValueError("operation already exists")
            self._items[operation.id] = operation
            return operation

    def get(self, operation_id: str) -> Optional[Operation]:
        with self._lock:
            return self._items.get(operation_id)

    def approve(self, operation_id: str, ttl_seconds: int = 300) -> Operation:
        with self._lock:
            operation = self._require(operation_id)
            operation.approve(ttl_seconds)
            return operation

    def execute_once(self, operation_id: str, action: str, payload: dict) -> str:
        with self._lock:
            operation = self._require(operation_id)

            if operation.execution_id:
                return operation.execution_id

            operation.begin_execution(action, payload)
            execution_id = f"exec-{operation.id}"
            operation.mark_executed(execution_id)
            self._executions[operation.id] = execution_id
            return execution_id

    def _require(self, operation_id: str) -> Operation:
        operation = self._items.get(operation_id)
        if operation is None:
            raise KeyError(operation_id)
        return operation
