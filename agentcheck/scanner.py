from __future__ import annotations

import ast
import re
from pathlib import Path

TEXT_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".md"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build"}


def _files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts) and p.suffix.lower() in TEXT_EXTENSIONS:
            yield p


def scan_repo(path: str) -> dict:
    root = Path(path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {root}")

    files = list(_files(root))
    text = "\n".join(_safe_read(p) for p in files)
    return {
        "path": str(root),
        "file_count": len(files),
        "has_readme": (root / "README.md").exists(),
        "has_pyproject": (root / "pyproject.toml").exists(),
        "has_requirements": (root / "requirements.txt").exists(),
        "has_package_json": (root / "package.json").exists(),
        "has_tests": any("test" in p.name.lower() or "tests" in p.parts for p in files),
        "has_ci": any(p.parts[-2:] == (".github", "workflows") for p in files if len(p.parts) >= 2),
        "tool_mentions": _count_patterns(text, ["tool_call", "function_call", "tools", "mcp", "function"]),
        "external_content_mentions": _count_patterns(text, ["httpx", "requests", "fetch(", "webhook", "rss", "url"]),
        "approval_mentions": _count_patterns(text, ["approval", "approve", "human", "confirm"]),
        "retry_mentions": _count_patterns(text, ["retry", "backoff", "tenacity"]),
        "logging_mentions": _count_patterns(text, ["logging", "logger", "audit_log", "telemetry", "trace"]),
        "secret_risk": _find_secret_risks(files),
        "python_ast": _python_summary(files),
    }


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:2_000_000]
    except OSError:
        return ""


def _count_patterns(text: str, patterns: list[str]) -> int:
    low = text.lower()
    return sum(low.count(p.lower()) for p in patterns)


def _find_secret_risks(files) -> list[str]:
    patterns = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"'][^\"']{8,}[\"']"),
    ]
    hits = []
    for p in files:
        content = _safe_read(p)
        if any(rx.search(content) for rx in patterns):
            hits.append(str(p))
    return hits[:20]


def _python_summary(files) -> dict:
    functions = 0
    imports = 0
    for p in files:
        if p.suffix != ".py":
            continue
        try:
            tree = ast.parse(_safe_read(p))
        except SyntaxError:
            continue
        functions += sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        imports += sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    return {"functions": functions, "imports": imports}
