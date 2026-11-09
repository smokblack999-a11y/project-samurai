"""Deterministic, intentionally small security heuristics for AEGIS.

These rules are triage signals, not proof of exploitability. Findings include a
short redacted source line so a reviewer can reproduce or dismiss each signal.
"""
import re

RULES = [
    {
        "id": "AEGIS-PY-001",
        "pattern": re.compile(r"\beval\s*\("),
        "title": "Dynamic code evaluation detected",
        "severity": "high",
        "cwe": "CWE-95",
        "impact": "If attacker-controlled data reaches this expression, arbitrary code may execute in the application's context.",
        "remediation": "Avoid eval; use an explicit parser, allowlisted operation map, or safe data format.",
    },
    {
        "id": "AEGIS-PY-002",
        "pattern": re.compile(r"\bsubprocess\.(?:run|Popen|call|check_output)\s*\(.*\bshell\s*=\s*True"),
        "title": "Subprocess invocation enables shell interpretation",
        "severity": "high",
        "cwe": "CWE-78",
        "impact": "If untrusted values are interpolated into the command, shell metacharacters may alter the executed command.",
        "remediation": "Prefer an argument list with shell=False; validate and allowlist every argument.",
    },
    {
        "id": "AEGIS-TLS-001",
        "pattern": re.compile(r"(?i)\bverify\s*=\s*False\b"),
        "title": "TLS certificate verification is disabled",
        "severity": "high",
        "cwe": "CWE-295",
        "impact": "The client may accept an untrusted certificate and become vulnerable to machine-in-the-middle interception.",
        "remediation": "Keep certificate verification enabled; configure the correct CA bundle for private PKI.",
    },
    {
        "id": "AEGIS-CONFIG-001",
        "pattern": re.compile(r"(?i)^\s*DEBUG\s*=\s*True\b"),
        "title": "Debug mode appears enabled",
        "severity": "medium",
        "cwe": "CWE-489",
        "impact": "Debug mode can expose diagnostics or sensitive implementation details if enabled in a deployed environment.",
        "remediation": "Disable debug mode in production and set it through an environment-specific configuration.",
    },
]

_SECRET_LITERAL = re.compile(
    r"""(?i)\b(?:api[_-]?key|client[_-]?secret|password|passwd|token|secret)\b\s*[:=]\s*['"][^'"]{8,}['"]"""
)
_PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


def _redact_line(line: str) -> str:
    line = _SECRET_LITERAL.sub("[REDACTED_ASSIGNMENT]", line)
    if _PRIVATE_KEY.search(line):
        return "[REDACTED_PRIVATE_KEY_LINE]"
    return line[:240]


def scan_static(content: str, artifact_type: str) -> list[dict]:
    if artifact_type not in {"source_code", "configuration"}:
        return []
    findings = []
    seen = set()
    for line_number, line in enumerate(content.splitlines(), start=1):
        for rule in RULES:
            if rule["pattern"].search(line):
                key = (rule["id"], line_number)
                if key in seen:
                    continue
                seen.add(key)
                findings.append({
                    "title": rule["title"],
                    "severity": rule["severity"],
                    "confidence": "medium",
                    "evidence": f"Line {line_number}: {_redact_line(line.strip())}",
                    "impact": rule["impact"],
                    "remediation": rule["remediation"],
                    "cwe": rule["cwe"],
                    "source": "static_rule",
                    "rule_id": rule["id"],
                })
        if _SECRET_LITERAL.search(line) or _PRIVATE_KEY.search(line):
            key = ("AEGIS-SECRET-001", line_number)
            if key not in seen:
                seen.add(key)
                findings.append({
                    "title": "Potential hard-coded credential or private-key material",
                    "severity": "high",
                    "confidence": "medium",
                    "evidence": f"Line {line_number}: {_redact_line(line.strip())}",
                    "impact": "A committed credential may be reused by an unauthorized party if it remains valid.",
                    "remediation": "Revoke and rotate the credential, remove it from source history where appropriate, and use a managed secret store.",
                    "cwe": "CWE-798",
                    "source": "static_rule",
                    "rule_id": "AEGIS-SECRET-001",
                })
    return findings
