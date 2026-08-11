from __future__ import annotations
from hmac import compare_digest


def valid_api_key(provided: str | None, expected: str | None) -> bool:
    if not provided or not expected:
        return False
    return compare_digest(provided, expected)
