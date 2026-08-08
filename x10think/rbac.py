from __future__ import annotations

ROLE_PERMISSIONS = {
    "viewer": {"read"},
    "operator": {"read", "approve"},
    "admin": {"read", "approve", "manage_policy"},
}


def can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
