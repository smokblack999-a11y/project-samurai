from __future__ import annotations

import json
import sys
from pathlib import Path

import argparse

from .report import write_html, write_json
from .scanner import scan_repo


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="agentcheck", description="Deterministic agent production-readiness scanner")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="scan a repository")
    scan.add_argument("path", nargs="?", default=".")
    scan.add_argument("--format", choices=("summary", "json", "html"), default="summary")
    scan.add_argument("--json-out", default="agentcheck.json")
    scan.add_argument("--html-out", default="agentcheck.html")
    scan.add_argument("--strict", action="store_true", help="exit non-zero on high/critical findings")

    args = parser.parse_args(argv)
    if args.command == "scan":
        result = scan_repo(args.path)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.format == "html":
            write_html(result, args.html_out)
            print(f"HTML report: {Path(args.html_out).resolve()}")
        else:
            print(f"AgentCheck v2: {result['status']} {result['score']}/100")
            print(f"Files: {result['files_scanned']} | Findings: {len(result['findings'])}")
            for f in result["findings"]:
                location = f["file"] + (f":{f['line']}" if f.get("line") else "")
                print(f"[{f['severity'].upper():8}] {f['rule_id']} {location} — {f['title']}")
        write_json(result, args.json_out)
        if args.strict and any(f["severity"] in {"critical", "high"} for f in result["findings"]):
            return 1
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
