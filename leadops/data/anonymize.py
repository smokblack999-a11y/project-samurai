from __future__ import annotations
import re

PATTERNS=[
 (re.compile(r"@[A-Za-z0-9_]{5,}"), "[HANDLE]"),
 (re.compile(r"\+?\d[\d\s().-]{7,}\d"), "[PHONE]"),
 (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
]

def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text=pattern.sub(replacement, text)
    return text

if __name__ == "__main__":
    import sys
    print(redact(sys.stdin.read()))
