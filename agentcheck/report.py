from __future__ import annotations

import html
import json
from pathlib import Path


def build_report(meta: dict, findings: list[dict], score: int) -> dict:
    counts = {s: sum(f["severity"] == s for f in findings) for s in ("critical", "high", "medium", "low")}
    return {
        "schema_version": "0.1",
        "assessment": {
            "score": score,
            "score_semantics": "static assessment score; not probability of safety or success",
            "status": "review_required" if findings else "no_static_findings",
        },
        "repository": meta,
        "finding_counts": counts,
        "findings": findings,
    }


def write_json(report: dict, path: str) -> None:
    Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_html(report: dict, path: str) -> None:
    rows = []
    for f in report["findings"]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(f['severity'].upper())}</td>"
            f"<td>{html.escape(f['id'])}</td>"
            f"<td>{html.escape(f['title'])}</td>"
            f"<td>{html.escape(f['evidence'])}</td>"
            f"<td>{html.escape(f['impact'])}</td>"
            f"<td>{html.escape(f['fix'])}</td>"
            "</tr>"
        )
    body = "".join(rows) or '<tr><td colspan="6">No static findings.</td></tr>'
    score = report["assessment"]["score"]
    document = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>AgentCheck Report</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1400px;margin:40px auto;padding:0 20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}}th{{background:#f4f4f4}}.score{{font-size:42px;font-weight:700}}</style>
</head><body><h1>Agent Production Readiness</h1>
<div class="score">{score}/100</div>
<p>Static assessment only. It is not a probability of safety, security, or business success.</p>
<h2>Findings</h2><table><thead><tr><th>Severity</th><th>ID</th><th>Title</th><th>Evidence</th><th>Business impact</th><th>Recommended fix</th></tr></thead><tbody>{body}</tbody></table>
</body></html>"""
    Path(path).write_text(document, encoding="utf-8")
