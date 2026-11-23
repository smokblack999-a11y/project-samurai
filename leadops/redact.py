from __future__ import annotations
import re

PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
USERNAME = re.compile(r"(?<!\w)@[A-Za-z0-9_]{3,32}\b")


def redact(text: str) -> str:
    text = PHONE.sub("[PHONE]", text)
    text = EMAIL.sub("[EMAIL]", text)
    text = USERNAME.sub("[USERNAME]", text)
    return text[:10000]
