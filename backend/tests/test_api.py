from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "online"

def test_validation_rejects_empty_text():
    r = client.post("/api/v1/analyze/message", json={"message_id": "1", "text": ""})
    assert r.status_code == 422
