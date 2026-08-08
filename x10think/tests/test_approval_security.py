import time

import approval


def test_approval_has_expiry_and_fingerprint():
    item = approval.create("restart_service", {"service": "demo"})
    assert item["status"] == "pending"
    assert item["fingerprint"]
    assert item["expires_at"] > item["created_at"]


def test_expired_approval_cannot_be_decided():
    item = approval.create("restart_service", {"service": "demo2"})
    approval._APPROVALS[item["id"]]["expires_at"] = time.time() - 1
    current = approval.get(item["id"])
    assert current["status"] == "expired"
