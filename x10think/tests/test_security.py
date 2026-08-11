from __future__ import annotations

from pathlib import Path

from x10think.security import scan


def test_env_files_are_flagged(tmp_path: Path):
    (tmp_path / ".env").write_text("TOGETHER_API_KEY=not-a-real-key", encoding="utf-8")
    findings = scan(tmp_path)
    assert any(item["id"] == "env-file" and item["severity"] == "high" for item in findings)
