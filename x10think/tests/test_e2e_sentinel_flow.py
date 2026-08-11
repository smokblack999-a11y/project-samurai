from x10think.operation import Operation, OperationStatus
from x10think.operation_store import OperationStore


def test_sentinel_full_secure_flow():
    store = OperationStore()

    op = Operation(
        id="sentinel-demo-1",
        trace_id="trace-demo-1",
        action="restart_service",
        payload={"service": "backend"},
        risk_score=75,
        fingerprint=Operation.make_fingerprint(
            "restart_service", {"service": "backend"}
        ),
        status=OperationStatus.APPROVAL_REQUIRED,
    )

    store.put(op)

    approved = store.approve("sentinel-demo-1")
    assert approved.status == OperationStatus.APPROVED

    execution_id = store.execute_once(
        "sentinel-demo-1",
        "restart_service",
        {"service": "backend"},
    )

    assert execution_id == "exec-sentinel-demo-1"
    assert store.get("sentinel-demo-1").status == OperationStatus.EXECUTED

    store.get("sentinel-demo-1").start_verification()
    store.get("sentinel-demo-1").mark_verified(True)

    assert store.get("sentinel-demo-1").status == OperationStatus.VERIFIED
