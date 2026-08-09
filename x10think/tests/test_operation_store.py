import pytest

from x10think.operation import Operation, OperationStatus
from x10think.operation_store import OperationStore


def operation():
    return Operation(
        id="op-replay",
        trace_id="trace-replay",
        action="restart_service",
        payload={"service": "backend"},
        risk_score=70,
        fingerprint=Operation.make_fingerprint(
            "restart_service", {"service": "backend"}
        ),
        status=OperationStatus.APPROVAL_REQUIRED,
    )


def test_execute_once_is_idempotent():
    store = OperationStore()
    store.put(operation())
    store.approve("op-replay")

    first = store.execute_once(
        "op-replay", "restart_service", {"service": "backend"}
    )
    second = store.execute_once(
        "op-replay", "restart_service", {"service": "backend"}
    )

    assert first == second == "exec-op-replay"
    assert store.get("op-replay").status == OperationStatus.EXECUTED


def test_replay_with_modified_payload_is_rejected():
    store = OperationStore()
    store.put(operation())
    store.approve("op-replay")

    with pytest.raises(ValueError, match="fingerprint"):
        store.execute_once(
            "op-replay", "restart_service", {"service": "database"}
        )
