import pytest
from fastapi import HTTPException

from app import aegis
from app.aegis import (
    AnalysisRequest,
    AnalysisResult,
    Finding,
    _combine_findings,
    _cyber_access_program,
    redact_secrets,
    run_analysis,
)
from app.static_checks import scan_static


def test_secret_redaction_removes_common_credentials():
    raw = (
        "Authorization: Bearer abc.def.ghi "
        "api_key=sk-example-secret password: hunter2 "
        "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    )
    cleaned = redact_secrets(raw)
    assert "abc.def.ghi" not in cleaned
    assert "sk-example-secret" not in cleaned
    assert "hunter2" not in cleaned
    assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" not in cleaned
    assert "[REDACTED" in cleaned


def test_static_scanner_detects_tls_and_eval_without_leaking_secret():
    content = (
        "response = requests.get(url, verify=False)\n"
        "value = eval(user_input)\n"
        "API_KEY = 'very-secret-value-that-must-not-leak'\n"
    )
    findings = scan_static(content, "source_code")
    assert any(item["rule_id"] == "AEGIS-TLS-001" for item in findings)
    assert any(item["rule_id"] == "AEGIS-PY-001" for item in findings)
    secret_findings = [item for item in findings if item["rule_id"] == "AEGIS-SECRET-001"]
    assert secret_findings
    assert all("very-secret-value-that-must-not-leak" not in item["evidence"] for item in secret_findings)


def test_static_scanner_ignores_logs():
    assert scan_static("verify=False", "log") == []


def test_daybreak_is_blocked_outside_internal_workspace(monkeypatch):
    monkeypatch.setattr(aegis.settings, "AEGIS_CYBER_PROGRAM", "daybreak_blue", raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_SECURITY_ONLY", False, raising=False)
    with pytest.raises(HTTPException) as exc:
        _cyber_access_program("project-a")
    assert exc.value.status_code == 403


def test_standard_program_is_default_safe_path(monkeypatch):
    monkeypatch.setattr(aegis.settings, "AEGIS_CYBER_PROGRAM", "standard", raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_SECURITY_ONLY", False, raising=False)
    assert _cyber_access_program("project-a") == "standard"


def test_analysis_request_bounds_input():
    with pytest.raises(ValueError):
        AnalysisRequest(artifact_type="log", task="incident_triage", content="x" * 20001)


def test_analysis_requires_both_authorization_and_external_ai_approval():
    request = AnalysisRequest(
        artifact_type="source_code",
        task="code_review",
        content="print('hello')",
        authorized_to_submit=False,
        external_ai_processing_approved=False,
    )
    with pytest.raises(HTTPException) as exc:
        import asyncio
        asyncio.run(run_analysis(request, "pilot-project"))
    assert exc.value.status_code == 400


def test_daybreak_requires_explicit_internal_project_allowlist(monkeypatch):
    monkeypatch.setattr(aegis.settings, "AEGIS_CYBER_PROGRAM", "daybreak_blue", raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_SECURITY_ONLY", True, raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_PROJECT_IDS", {"internal-security"}, raising=False)
    with pytest.raises(HTTPException) as exc:
        _cyber_access_program("customer-project")
    assert exc.value.status_code == 403
    assert _cyber_access_program("internal-security") == "daybreak_blue"


def test_static_findings_are_merged_and_raise_risk_level():
    model = AnalysisResult(
        summary="Initial model triage",
        risk_level="low",
        findings=[
            Finding(
                title="Potential issue from model",
                severity="low",
                confidence="medium",
                evidence="Line 1: example",
                impact="Possible issue",
                remediation="Review it",
                cwe="CWE-0",
            )
        ],
        assumptions=[],
        recommended_tests=[],
        scope_warnings=[],
    )
    static = [{
        "title": "TLS certificate verification is disabled",
        "severity": "high",
        "confidence": "medium",
        "evidence": "Line 2: verify=False",
        "impact": "Possible MITM",
        "remediation": "Enable verification",
        "cwe": "CWE-295",
        "source": "static_rule",
        "rule_id": "AEGIS-TLS-001",
    }]
    result = _combine_findings(model, static)
    assert result.risk_level == "high"
    assert any(item.source == "static_rule" for item in result.findings)
    assert any("heuristic" in item.lower() for item in result.scope_warnings)
