from __future__ import annotations

SEVERITY_WEIGHT = {"critical": 10, "high": 7, "medium": 4, "low": 1, "info": 0}


def finding(check_id: str, severity: str, title: str, evidence: str, impact: str, fix: str) -> dict:
    return {
        "id": check_id,
        "severity": severity,
        "title": title,
        "evidence": evidence,
        "impact": impact,
        "fix": fix,
    }


def run_checks(meta: dict) -> list[dict]:
    out = []

    if meta["tool_mentions"] > 0 and meta["approval_mentions"] == 0:
        out.append(finding(
            "AGT-001", "high", "Tool use without visible approval boundary",
            f"Tool/function references detected ({meta['tool_mentions']}); no approval/confirmation signal found.",
            "An agent may perform consequential actions without an explicit human-control boundary.",
            "Document and enforce approval requirements for high-impact side effects; add tests for the boundary.",
        ))

    if meta["external_content_mentions"] > 0:
        out.append(finding(
            "AGT-002", "medium", "External-content attack surface",
            f"External/network/content signals detected ({meta['external_content_mentions']}).",
            "Untrusted content can influence agent context, tool selection, or downstream actions.",
            "Separate trusted instructions from external content and add adversarial evaluation cases.",
        ))

    if meta["tool_mentions"] > 0 and meta["logging_mentions"] == 0:
        out.append(finding(
            "AGT-003", "high", "Insufficient visible audit telemetry",
            "Tool-capable code detected without recognizable logging/telemetry signals.",
            "Failures and unauthorized or incorrect actions become difficult to investigate or reproduce.",
            "Record tool calls, actor/context, outcomes, errors and correlation IDs without logging secrets.",
        ))

    if meta["tool_mentions"] > 0 and meta["retry_mentions"] == 0:
        out.append(finding(
            "AGT-004", "medium", "No visible retry/backoff policy",
            "Tool/network signals exist but no retry/backoff implementation was detected.",
            "Transient failures can become brittle workflows or uncontrolled repeated actions.",
            "Define bounded retries, exponential backoff, idempotency expectations and terminal failure states.",
        ))

    if meta["secret_risk"]:
        out.append(finding(
            "AGT-005", "critical", "Possible hard-coded secret",
            "Potential credential-like literals were detected in source files.",
            "Credential exposure can enable unauthorized access and compromise downstream systems.",
            "Move secrets to a managed secret store/environment, rotate exposed credentials and add secret scanning to CI.",
        ))

    if not meta["has_tests"]:
        out.append(finding(
            "AGT-006", "high", "No recognizable test suite",
            "No test files were detected by the static scanner.",
            "Agent behavior can regress silently after model, prompt, tool or dependency changes.",
            "Add deterministic unit tests plus an agent regression/evaluation suite covering critical workflows.",
        ))

    if not meta["has_ci"]:
        out.append(finding(
            "AGT-007", "medium", "No recognizable CI workflow",
            "No .github/workflows files were detected.",
            "Checks may not run consistently before changes reach production.",
            "Run static checks, tests and agent evaluations on every pull request.",
        ))

    if meta["tool_mentions"] > 0 and meta["has_readme"] is False:
        out.append(finding(
            "AGT-008", "medium", "Missing operational documentation",
            "Tool-capable signals detected but README.md is absent.",
            "Operators and reviewers lack a clear description of capabilities and failure boundaries.",
            "Document agent purpose, tools, permissions, data flows, side effects and rollback procedures.",
        ))

    return out


def readiness_score(meta: dict, findings: list[dict]) -> int:
    # This is an assessment score, not a probability of safety or success.
    penalty = sum(SEVERITY_WEIGHT.get(f["severity"], 0) for f in findings)
    structural_bonus = sum([
        8 if meta["has_tests"] else 0,
        6 if meta["has_ci"] else 0,
        4 if meta["has_readme"] else 0,
    ])
    return max(0, min(100, 100 - penalty * 4 + structural_bonus))
