from x10think.trace_context import TraceContext


def test_trace_context_is_stable_and_unique():
    a = TraceContext.new()
    b = TraceContext.new()
    assert a.trace_id != b.trace_id
    assert a.audit_fields()["trace_id"] == a.trace_id
    assert a.workflow == "x10think-sentinel-analysis"
