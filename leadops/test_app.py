from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_buying():
    r = client.post('/api/v1/analyze/message', json={'text': 'Сколько стоит заказать сегодня?'})
    assert r.status_code == 200
    data = r.json()
    assert data['intent'] == 'buying'
    assert data['lead_score'] >= 90
    assert data['recommended_action'] == 'human_followup'

def test_information():
    r = client.post('/api/v1/analyze/message', json={'text': 'Как вы работаете?'})
    assert r.status_code == 200
    assert r.json()['intent'] == 'information'
