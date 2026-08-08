from audit import AuditLog
from audit_verify import verify


def test_audit_chain_detects_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path)
    log.record("test", value=1)
    log.record("test", value=2)
    ok, count = verify(path)
    assert ok is True
    assert count == 2

    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"value":1', '"value":999')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, count = verify(path)
    assert ok is False
    assert count == 0
