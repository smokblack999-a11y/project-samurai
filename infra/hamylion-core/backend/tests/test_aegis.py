import pytest
from fastapi import HTTPException
from app import aegis
from app.aegis import AnalysisRequest, _cyber_access_program, redact_secrets

def test_secret_redaction_removes_common_credentials():
    raw = "Authorization: Bearer abc.def.ghi\\napi_key=sk-example-secret password: hunter2"
    cleaned = redact_secrets(raw)
    assert "abc.def.ghi" not in cleaned
    assert "sk-example-secret" not in cleaned
    assert "hunter2" not in cleaned
    assert "[REDACTED]" in cleaned

def test_daybreak_is_blocked_outside_internal_workspace(monkeypatch):
    monkeypatch.setattr(aegis.settings, "AEGIS_CYBER_PROGRAM", "daybreak_blue", raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_SECURITY_ONLY", False, raising=False)
    with pytest.raises(HTTPException) as exc:
        _cyber_access_program()
    assert exc.value.status_code == 403

def test_standard_program_is_default_safe_path(monkeypatch):
    monkeypatch.setattr(aegis.settings, "AEGIS_CYBER_PROGRAM", "standard", raising=False)
    monkeypatch.setattr(aegis.settings, "AEGIS_INTERNAL_SECURITY_ONLY", False, raising=False)
    assert _cyber_access_program() == "standard"

def test_analysis_request_bounds_input():
    with pytest.raises(ValueError):
        AnalysisRequest(artifact_type="log", task="incident_triage", content="x" * 20001)
