from __future__ import annotations

import os
from fastapi import Header, HTTPException


def _tokens() -> dict[str, str]:
    out = {}
    for role, env_name in (("viewer", "X10_VIEWER_KEY"), ("operator", "X10_OPERATOR_KEY"), ("admin", "X10_ADMIN_KEY")):
        value = os.getenv(env_name)
        if value:
            out[value] = role
    return out


def require_role(authorization: str | None, minimum: str = "viewer") -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="authentication_required")
    role = _tokens().get(authorization[7:])
    ranks = {"viewer": 1, "operator": 2, "admin": 3}
    if not role or ranks[role] < ranks[minimum]:
        raise HTTPException(status_code=403, detail="insufficient_role")
    return role


def viewer_role(authorization: str | None = Header(default=None)) -> str:
    return require_role(authorization, "viewer")


def operator_role(authorization: str | None = Header(default=None)) -> str:
    return require_role(authorization, "operator")
