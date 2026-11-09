"""Codeberg RSS -> canonical HAMYLION event adapter."""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def _text(parent: ET.Element, name: str) -> str:
    node = parent.find(name)
    return (node.text or "").strip() if node is not None else ""


def _event_type(title: str) -> str:
    value = title.lower()
    if "выпуск" in value or "release" in value:
        return "codeberg.release.published"
    if "отправлен тег" in value or "tag" in value:
        return "codeberg.tag.created"
    if "изменения отправлены" in value or "commit" in value:
        return "codeberg.commit.pushed"
    if "задача" in value or "issue" in value:
        return "codeberg.issue.updated"
    return "codeberg.activity"


def parse_codeberg_rss(xml: str, repository: str | None = None) -> list[dict]:
    root = ET.fromstring(xml)
    result = []
    for item in root.findall(".//item"):
        title = _text(item, "title")
        link = _text(item, "link")
        guid = _text(item, "guid") or link
        author = _text(item, "author")
        published = _text(item, "pubDate")
        try:
            timestamp = parsedate_to_datetime(published).astimezone(timezone.utc).isoformat() if published else datetime.now(timezone.utc).isoformat()
        except (TypeError, ValueError):
            timestamp = datetime.now(timezone.utc).isoformat()

        repo = repository
        if not repo and link:
            match = re.search(r"codeberg\.org/([^/]+/[^/]+)", link)
            repo = match.group(1) if match else "unknown"

        external_id = hashlib.sha256(guid.encode("utf-8")).hexdigest()
        result.append({
            "idempotency_key": f"codeberg:{external_id}",
            "type": _event_type(title),
            "payload": {
                "source": "codeberg",
                "external_id": guid,
                "repository": repo or "unknown",
                "title": title,
                "actor": author,
                "url": link,
                "timestamp": timestamp,
            },
        })
    return result
