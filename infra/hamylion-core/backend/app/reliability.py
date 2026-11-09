import hashlib
import hmac
import json
import time


def backoff_seconds(attempt: int, base: float, maximum: float) -> float:
    if attempt <= 0:
        return 0.0
    return min(maximum, base * (2 ** (attempt - 1)))


def event_fingerprint(event: dict) -> str:
    raw = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sign_payload(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = sign_payload(secret, body)
    return bool(signature) and hmac.compare_digest(expected, signature)


def retry_at(attempt: int, base: float, maximum: float) -> float:
    return time.time() + backoff_seconds(attempt, base, maximum)
