import pytest
from pydantic import ValidationError
from ai_schema import AIAnalysis

def test_ai_schema_rejects_extra_fields():
    with pytest.raises(ValidationError):
        AIAnalysis(summary="ok", severity="low", unexpected="x")
