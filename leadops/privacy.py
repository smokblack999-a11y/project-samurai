from hashlib import sha256


def fingerprint_message(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def redact_for_export(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    return compact[:limit] + ("…" if len(compact) > limit else "")
