import json

from x10think.sentinel_cli import run_audit


def test_run_audit_writes_report(tmp_path):
    output = tmp_path / "report.json"
    assert run_audit(output) == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["report_version"] == "1.0"
    assert report["operation"]["id"].startswith("audit-")
    assert report["summary"]["audit_events"] >= 2
    assert (tmp_path / "report.audit.jsonl").exists()
