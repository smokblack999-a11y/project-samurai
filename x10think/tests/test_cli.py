import json

from x10think.cli import build_local_report, collect_telemetry


def test_collect_telemetry_has_core_fields():
    data = collect_telemetry()
    assert data["hostname"]
    assert data["python"]
    assert 0 <= data["disk_used_ratio"] <= 1


def test_build_local_report_is_verified():
    report = build_local_report()
    assert report["report_version"] == "1.0"
    assert report["operation"]["action"] == "health"
    assert report["operation"]["status"] == "verified"
    assert report["operation"]["risk_score"] == 5
    assert len(report["audit"]) == 2
    json.dumps(report)


def test_local_reports_use_unique_operation_ids():
    first = build_local_report()
    second = build_local_report()
    assert first["operation"]["id"] != second["operation"]["id"]
    assert first["operation"]["trace_id"] != second["operation"]["trace_id"]
