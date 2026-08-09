import os
import pytest
from fastapi import HTTPException
from auth import require_role


def test_missing_auth_is_rejected():
    with pytest.raises(HTTPException) as exc:
        require_role(None)
    assert exc.value.status_code == 401


def test_operator_cannot_act_as_admin(monkeypatch):
    monkeypatch.setenv("X10_OPERATOR_KEY", "op")
    monkeypatch.setenv("X10_ADMIN_KEY", "admin")
    with pytest.raises(HTTPException) as exc:
        require_role("Bearer op", "admin")
    assert exc.value.status_code == 403
