import time

import pytest

from x10think.operation import Operation, OperationStatus


def make_operation():
    return Operation(
        id="op-1",
        trace_id="trace-1",
        action="restart_service",
        payload={"service": "backend"},
        risk_score=70,
        fingerprint=Operation.make_fingerprint(
            "restart_service", {"service": "backend"}
        ),
        status=OperationStatus.APPROVAL_REQUIRED,
    )


def test_approval_binds_exact_payload():
    op = make_operation()
    op.approve(ttl_seconds=60)
    assert op.status == OperationStatus.APPROVED
    op.begin_execution("restart_service", {"service": "backend"})
    assert op.status == OperationStatus.EXECUTING


def test_modified_payload_is_rejected():
    op = make_operation()
    op.approve(ttl_seconds=60)
    with pytest.raises(ValueError, match="fingerprint"):
        op.begin_execution("restart_service", {"service": "database"})


def test_expired_approval_is_rejected():
    op = make_operation()
    op.approve(ttl_seconds=1)
    assert not op.revalidate(
        "restart_service", {"service": "backend"}, now=time.time() + 2
    )
    assert op.status == OperationStatus.EXPIRED


def test_full_lifecycle():
    op = make_operation()
    op.approve()
    op.begin_execution("restart_service", {"service": "backend"})
    op.mark_executed("exec-1")
    op.start_verification()
    op.mark_verified(True)
    assert op.status == OperationStatus.VERIFIED


def test_invalid_transition_is_rejected():
    op = make_operation()
    with pytest.raises(ValueError):
        op.mark_executed("exec-1")
