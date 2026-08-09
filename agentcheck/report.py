from __future__ import annotations

import json
from html import escape
from pathlib import Path


def write_json(result: dict, output: str) -> None:
    Path(output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def write_html(result: dict, output: str) -> None:
    rows = []
    for f in result["findings"]:
        rows.append(
            "<tr>"
            f"<td>{escape(f['rule_id'])}</td>"
            f"<td>{escape(f['severity'].upper())}</td>"
            f"<td>{escape(f['title'])}</td>"
            f"<td>{escape(f['file'])}:{f.get('line') or ''}</td>"
            f"<td>{escape(f['evidence'])}</td>"
            f"<td>{escape(f['remediation'])}</td>"
            "</tr>"
        )
    status = escape(result["status"])
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>AgentCheck Report</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1500px;margin:40px auto;padding:0 20px}}
.score{{font-size:48px;font-weight:800}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #ddd;vertical-align:top;text-align:left}}code{{word-break:break-all}}
</style></head><body>
<h1>AgentCheck v2</h1><div class="score">{result['score']}/100</div>
<p>Status: <strong>{status}</strong></p>
<p>Files: {result['files_scanned']} · Findings: {len(result['findings'])} · Fingerprint: <code>{escape(result['content_fingerprint'])}</code></p>
<table><thead><tr><th>Rule</th><th>Severity</th><th>Finding</th><th>Location</th><th>Evidence</th><th>Remediation</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>"""
    Path(output).write_text(html, encoding="utf-8")
