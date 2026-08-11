from x10think.operation import Operation, OperationStatus
from x10think.report import build_report, report_json


def test_report_contains_operation_and_audit():
    op = Operation(
        id="op-1",
        trace_id="trace-1",
        action="restart_service",
        payload={"service": "backend"},
        risk_score=70,
        fingerprint=Operation.make_fingerprint("restart_service", {"service": "backend"}),
        status=OperationStatus.VERIFIED,
        execution_id="exec-op-1",
    )
    events = [{"event": "approved"}, {"event": "verified"}]
    report = build_report(op, events)

    assert report["operation"]["id"] == "op-1"
    assert report["operation"]["trace_id"] == "trace-1"
    assert report["operation"]["execution_id"] == "exec-op-1"
    assert report["summary"]["audit_events"] == 2
    assert "hash-chain" in report["summary"]["integrity_claim"]
    assert '"operation"' in report_json(op, events)
