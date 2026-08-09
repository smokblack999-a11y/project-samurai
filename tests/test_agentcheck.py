from agentcheck.scanner import readiness_score, scan_repo


def test_high_finding_reduces_score(tmp_path):
    p = tmp_path / "agent.py"
    p.write_text("import subprocess\nsubprocess.run('echo x', shell=True)\n", encoding="utf-8")
    result = scan_repo(str(tmp_path))
    assert any(f["rule_id"] == "TOOL-001" for f in result["findings"])
    assert result["score"] < 100


def test_secret_is_critical(tmp_path):
    p = tmp_path / "config.py"
    p.write_text("KEY='sk-abcdefghijklmnopqrstuvwxyz123456'\n", encoding="utf-8")
    result = scan_repo(str(tmp_path))
    findings = [f for f in result["findings"] if f["rule_id"] == "SEC-001"]
    assert findings
    assert findings[0]["severity"] == "critical"


def test_clean_repository_has_full_base_score(tmp_path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    result = scan_repo(str(tmp_path))
    assert readiness_score([]) == 100.0
    assert result["score"] == 100.0
