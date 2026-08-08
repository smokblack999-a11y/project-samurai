from schemas import AIAnalysis


def test_valid_analysis_schema():
    result = AIAnalysis.model_validate({
        "summary": "Disk usage is elevated.",
        "severity": "medium",
        "findings": [{"title": "Disk usage", "severity": "medium", "evidence": "82% used"}],
        "next_steps": ["Review large files"],
    })
    assert result.severity == "medium"


def test_invalid_severity_rejected():
    try:
        AIAnalysis.model_validate({"summary": "x", "severity": "danger", "findings": [], "next_steps": []})
    except ValueError:
        return
    raise AssertionError("invalid severity was accepted")
