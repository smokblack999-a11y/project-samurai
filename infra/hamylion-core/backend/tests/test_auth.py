import pytest

from app.auth import validate_api_key
from app.config import settings

@pytest.mark.asyncio
async def test_bootstrap_api_key_maps_to_default_project(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "bootstrap-secret")
    assert await validate_api_key("bootstrap-secret") == "default-project"

@pytest.mark.asyncio
async def test_missing_api_key_is_rejected():
    with pytest.raises(Exception):
        await validate_api_key(None)
