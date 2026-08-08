import os

os.environ["X10_VIEWER_KEY"] = "viewer-test"
os.environ["X10_OPERATOR_KEY"] = "operator-test"
os.environ["X10_ADMIN_KEY"] = "admin-test"

from fastapi.testclient import TestClient
from api import app

client = TestClient(app)
VIEWER = {"Authorization": "Bearer viewer-test"}
OPERATOR = {"Authorization": "Bearer operator-test"}


def test_health_is_public():
    assert client.get("/health").status_code == 200


def test_approval_requires_authentication():
    assert client.post("/approvals", json={"action": "health"}).status_code == 401


def test_viewer_cannot_execute():
    assert client.post("/approvals/nope/execute", headers=VIEWER).status_code == 403


def test_operator_can_approve_health_and_execute_once():
    created = client.post("/approvals", headers=VIEWER, json={"action": "health"})
    assert created.status_code == 200
    approval_id = created.json()["id"]
    assert created.json()["status"] == "approved"

    executed = client.post(f"/approvals/{approval_id}/execute", headers=OPERATOR)
    assert executed.status_code == 200

    replay = client.post(f"/approvals/{approval_id}/execute", headers=OPERATOR)
    assert replay.status_code == 400
    assert replay.json()["detail"] == "already_executed"


def test_forbidden_action_never_creates_approval():
    response = client.post("/approvals", headers=VIEWER, json={"action": "execute_shell", "payload": {"cmd": "id"}})
    assert response.status_code == 400
    assert response.json()["detail"] == "action_forbidden"
