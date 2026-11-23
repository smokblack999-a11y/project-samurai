from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_buying_message():
    r = client.post(
        "/api/v1/analyze/message",
        json={"text": "Сколько стоит заказать услугу?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "buying"
    assert data["lead_score"] >= 78
    assert data["recommended_action"] == "human_followup"


def test_system_status():
    r = client.get("/api/v1/system/status")
    assert r.status_code == 200
    assert r.json()["service"] == "telegram-leadops"
    assert "metrics" in r.json()


def test_normalized_telegram_ingest():
    r = client.post(
        "/api/v1/ingest/telegram",
        json={
            "source": "telegram",
            "account_id": "demo",
            "chat_id": "123",
            "message_id": "456",
            "text": "Хочу заказать услугу сегодня",
            "received_at": 1760000000,
        },
    )
    assert r.status_code == 200
    assert r.json()["accepted"] is True
    assert r.json()["decision"]["intent"] == "buying"
