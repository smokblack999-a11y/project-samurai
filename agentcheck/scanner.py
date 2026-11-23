from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path


SEVERITY_PENALTY = {"critical": 30, "high": 20, "medium": 10, "low": 5, "info": 0}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    confidence: int
    file: str
    line: int | None
    evidence: str
    impact: str
    remediation: str
    verification: str

    def to_dict(self) -> dict:
        return asdict(self)


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
TEXT_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".env", ".ini", ".cfg"}


def _files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            if p.suffix.lower() in TEXT_EXTENSIONS or p.name.startswith(".env"):
                yield p


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _line(text: str, match: re.Match) -> int:
    return text.count("\n", 0, match.start()) + 1


def scan_repo(path: str) -> dict:
    root = Path(path).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Repository directory not found: {root}")

    findings: list[Finding] = []
    files = list(_files(root))
    all_text = []

    for file in files:
        text = _read(file)
        all_text.append(text)
        findings.extend(_scan_file(root, file, text))

    findings = _dedupe(findings)
    score = readiness_score(findings)
    digest = hashlib.sha256("".join(all_text).encode()).hexdigest()[:16]

    return {
        "schema_version": "agentcheck/v2",
        "repo": str(root),
        "files_scanned": len(files),
        "content_fingerprint": digest,
        "score": score,
        "status": "PASS" if score >= 80 and not any(f.severity in {"critical", "high"} for f in findings) else "REVIEW",
        "findings": [f.to_dict() for f in findings],
    }


def _scan_file(root: Path, file: Path, text: str) -> list[Finding]:
    out: list[Finding] = []
    rel = str(file.relative_to(root))
    agent_context = bool(re.search(r"(?:agent|llm|model|mcp|tool_call|function_call|execute_tool|call_tool)", text, re.I))

    def add(rule, title, severity, confidence, evidence, impact, remediation, verification, line=None):
        out.append(Finding(rule, title, severity, confidence, rel, line, evidence, impact, remediation, verification))

    secret_patterns = [
        (r"sk-[A-Za-z0-9_-]{20,}", "OpenAI-style API key"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    ]
    for pattern, name in secret_patterns:
        m = re.search(pattern, text)
        if m:
            add("SEC-001", f"Potential {name} exposed", "critical", 95,
                f"credential-like token matched at line {_line(text, m)}",
                "A leaked credential can enable unauthorized access.",
                "Remove and rotate the secret; use a secret manager or environment injection.",
                "Re-run AgentCheck and confirm no credential-like token remains.", _line(text, m))

    # Only elevate execution primitives when they are part of an agent/tool context.
    # Generic build/install scripts legitimately use subprocess and must not be treated
    # as agent execution risks by default.
    execution_match = re.search(r"(?:subprocess\.|os\.system\(|shell\s*=\s*True|\bexec\(|\beval\()", text, re.I)
    if execution_match and agent_context:
        add("TOOL-001", "Potential unrestricted execution surface", "high", 88,
            "agent/tool context contains a shell/process/eval primitive",
            "An agent connected to unrestricted execution can cross a high-impact side-effect boundary.",
            "Expose only explicit tools with allow-listed operations, validated arguments and least privilege.",
            "Add a negative test proving forbidden commands are rejected.", _line(text, execution_match))

    if re.search(r"\b(?:function_call|tool_call|tools|mcp|execute_tool|call_tool)\b", text, re.I):
        if not re.search(r"(?:allowlist|allow_list|approved_tools|allowed_tools|permission|authorize|authorization)", text, re.I):
            add("ACCESS-001", "Tool boundary lacks an obvious authorization control", "high", 78,
                "tool/MCP/function-call vocabulary found without an adjacent allow-list or authorization signal",
                "An agent may invoke a capability outside its intended permission boundary.",
                "Define explicit tool permissions and enforce them server-side before execution.",
                "Test an unauthorized tool call and assert deterministic rejection.")

    if re.search(r"(?:tool|function|mcp).*?(?:input|args|arguments|parameters)", text, re.I | re.S):
        if not re.search(r"(?:schema|validate|validator|pydantic|zod|jsonschema)", text, re.I):
            add("TOOL-002", "Tool input validation is not evident", "high", 72,
                "tool/function input signals found without schema/validation signal",
                "Malformed or adversarial arguments can reach side-effecting tools.",
                "Validate tool arguments against a strict schema before execution.",
                "Add malformed-input tests and require validation failure before execution.")

    if re.search(r"(?:tool|function|mcp).*?(?:result|output|response)", text, re.I | re.S):
        if not re.search(r"(?:validate|schema|parse|sanitize|structured)", text, re.I):
            add("TOOL-003", "Tool output validation is not evident", "medium", 65,
                "tool output/result signal without clear validation",
                "Untrusted tool output can influence subsequent agent decisions.",
                "Parse and validate tool outputs before passing them into privileged logic.",
                "Inject invalid tool output and assert safe handling.")

    if re.search(r"(?:human.?approval|approval_required|require_approval|human_in_the_loop)", text, re.I) is None:
        if re.search(r"(?:delete|refund|purchase|send_email|send_message|deploy|payment|write_file|execute)", text, re.I):
            add("APPROVAL-001", "Sensitive side-effect detected without obvious human approval boundary", "high", 82,
                "sensitive action vocabulary found without approval signal",
                "Autonomous execution of irreversible actions can create material business impact.",
                "Require human approval or an equivalent policy gate for sensitive actions.",
                "Attempt the sensitive action in test mode and assert approval is required.")

    if re.search(r"(?:delete|refund|purchase|payment|deploy|send_email|send_message|write_file)", text, re.I):
        if not re.search(r"(?:idempot|dry.?run|transaction|rollback|confirm)", text, re.I):
            add("SIDEFX-001", "Side-effecting workflow lacks an obvious safety boundary", "medium", 76,
                "irreversible/external side-effect signal without idempotency, dry-run or confirmation signal",
                "Retries or repeated agent decisions can duplicate external actions.",
                "Add idempotency keys, dry-run support and explicit confirmation for irreversible operations.",
                "Run the same action twice and verify the external effect occurs at most once.")

    if re.search(r"(?:prompt|system_message|instructions|user_input)", text, re.I):
        if re.search(r"(?:web|url|http|document|search|retriev|rss|feed)", text, re.I):
            if not re.search(r"(?:untrusted|sanitize|isolate|quote|boundary|treat.*data)", text, re.I):
                add("INJECT-001", "External content reaches prompt-sensitive logic without an obvious trust boundary", "high", 75,
                    "prompt/instruction signals coexist with external-content ingestion",
                    "Untrusted content can influence agent instructions or tool selection.",
                    "Separate data from instructions, constrain tool decisions and treat retrieved content as untrusted.",
                    "Add a fixture containing instruction-like external content and assert it cannot change tool policy.")

    if re.search(r"(?:requests\.|httpx\.|urllib|fetch\(|axios|rss|feedparser|webbrowser)", text, re.I):
        if agent_context:
            add("CONTENT-001", "External content is part of an agent data path", "medium", 68,
                "network/content retrieval and agent/model/tool signals detected",
                "External data should be considered untrusted input to agent reasoning.",
                "Document trust boundaries and enforce content/tool separation before model decisions.",
                "Test with adversarial external content and verify policy remains unchanged.")

    if re.search(r"(?:logging|logger|structlog|loguru|print\(|console\.log)", text, re.I) is None:
        if agent_context:
            add("AUDIT-001", "No obvious audit logging signal", "medium", 70,
                "agent/tool/model code detected without logging signal",
                "Without traceable events, incidents and regressions are difficult to investigate.",
                "Record actor, tool, decision, outcome and correlation identifiers without secrets.",
                "Execute a tool call and verify an auditable event is emitted.")

    if re.search(r"(?:except\s*:\s*pass|except Exception:\s*pass|catch\s*\([^)]*\)\s*\{\s*\})", text, re.I):
        add("ERROR-001", "Exception path appears to discard errors", "medium", 84,
            "exception handler contains an empty/pass-style recovery",
            "Silent failures can turn tool/model errors into incorrect agent state.",
            "Handle expected failures explicitly and preserve diagnostic context.",
            "Inject an exception and verify it produces a controlled, observable outcome.")

    if re.search(r"(?:httpx|requests|fetch\(|axios|openai|anthropic)", text, re.I):
        if not re.search(r"(?:timeout|AbortController|deadline)", text, re.I):
            add("RETRY-001", "External call has no obvious timeout/deadline", "medium", 80,
                "external API call signal without timeout/deadline signal",
                "Hung dependencies can stall an agent workflow and consume resources.",
                "Set explicit timeouts/deadlines and bounded retry/backoff policies.",
                "Simulate a slow dependency and verify the call terminates within the configured deadline.")

    if agent_context:
        if not re.search(r"(?:eval|evaluation|grader|assert.*response|test.*agent|golden|benchmark)", text, re.I):
            add("EVAL-001", "No obvious agent evaluation harness", "medium", 62,
                "agent/model usage found without evaluation/test signal",
                "Behavioral regressions can ship without a measurable acceptance criterion.",
                "Create deterministic evaluation cases for critical tasks and failure modes.",
                "Run the evaluation suite and require a minimum pass threshold.")

        if not re.search(r"(?:pytest|unittest|vitest|jest|test_.*agent|agent.*test)", text, re.I):
            add("REGRESSION-001", "Agent regression tests are not evident", "medium", 64,
                "agent/tool/model code found without test-framework or agent-test signal",
                "Changes to prompts, models or tools can silently change behavior.",
                "Add golden scenarios covering success, refusal, tool selection and side effects.",
                "Change a controlled prompt/tool dependency and require the regression suite to detect it.")

        if not re.search(r"(?:trace|tracing|telemetry|opentelemetry|metrics|span|observability)", text, re.I):
            add("OBS-001", "Runtime observability is not evident", "low", 60,
                "agent/tool/model code found without tracing or telemetry signal",
                "Latency, failures and tool behavior cannot be monitored reliably in production.",
                "Capture structured traces, latency, errors and tool outcomes with sensitive data redaction.",
                "Execute a representative workflow and verify a trace/metric is emitted.")

    return out


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen = set()
    result = []
    for f in findings:
        key = (f.rule_id, f.file, f.line)
        if key not in seen:
            seen.add(key)
            result.append(f)
    return result


def readiness_score(findings: list[Finding]) -> float:
    penalty = sum(SEVERITY_PENALTY[f.severity] * f.confidence / 100 for f in findings)
    return round(max(0.0, min(100.0, 100.0 - penalty)), 2)
