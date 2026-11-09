from __future__ import annotations

import argparse
import json
import sys

from .evaluations import readiness_score, run_checks
from .report import build_report, write_html, write_json
from .scanner import scan_repo


def main() -> int:
    parser = argparse.ArgumentParser(prog="agentcheck", description="Agent Production Readiness static scanner")
    parser.add_argument("path", help="Path to an agent repository")
    parser.add_argument("--json", dest="json_path", help="Write JSON report")
    parser.add_argument("--html", dest="html_path", help="Write HTML report")
    args = parser.parse_args()

    try:
        meta = scan_repo(args.path)
        findings = run_checks(meta)
        score = readiness_score(meta, findings)
        report = build_report(meta, findings, score)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2))
    if args.json_path:
        write_json(report, args.json_path)
        print(f"JSON report: {args.json_path}")
    if args.html_path:
        write_html(report, args.html_path)
        print(f"HTML report: {args.html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
