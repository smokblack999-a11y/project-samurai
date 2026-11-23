from pathlib import Path

from agentcheck.evaluations import readiness_score, run_checks
from agentcheck.scanner import scan_repo


def test_scanner_detects_agent_signals(tmp_path: Path):
    (tmp_path / "README.md").write_text("agent", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci", encoding="utf-8")
    (tmp_path / "agent.py").write_text(
        "import httpx\n\ndef function_call():\n    return httpx.get('https://example.com')\n",
        encoding="utf-8",
    )
    meta = scan_repo(str(tmp_path))
    assert meta["has_ci"] is True
    assert meta["tool_mentions"] > 0
    assert meta["external_content_mentions"] > 0


def test_checks_return_findings_without_tests(tmp_path: Path):
    (tmp_path / "agent.py").write_text("def tool_call(): pass", encoding="utf-8")
    meta = scan_repo(str(tmp_path))
    findings = run_checks(meta)
    ids = {f["id"] for f in findings}
    assert "AGT-001" in ids
    assert "AGT-006" in ids
    assert 0 <= readiness_score(meta, findings) <= 100
