from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_ingest_message():
    update = {
        "@type": "updateNewMessage",
        "message": {
            "id": 123,
            "chat_id": 456,
            "sender_id": {"@type": "messageSenderUser", "user_id": 789},
            "content": {
                "@type": "messageText",
                "text": {"@type": "formattedText", "text": "Сколько стоит заказать сегодня?"},
            },
        },
    }
    r = client.post('/api/v1/ingest/telegram', json={"update": update})
    assert r.status_code == 200
    data = r.json()
    assert data['accepted'] is True
    assert data['event_id'] == 'tg:456:123'
    assert data['decision']['message_id'] == '123'


def test_duplicate_is_idempotent():
    update = {
        "@type": "updateNewMessage",
        "message": {
            "id": 124,
            "chat_id": 456,
            "content": {
                "@type": "messageText",
                "text": {"@type": "formattedText", "text": "Цена?"},
            },
        },
    }
    first = client.post('/api/v1/ingest/telegram', json={"update": update}).json()
    second = client.post('/api/v1/ingest/telegram', json={"update": update}).json()
    assert first['duplicate'] is False
    assert second['duplicate'] is True
