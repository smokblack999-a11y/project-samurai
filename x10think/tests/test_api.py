import os

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_status_endpoint():
    response = client.get('/status')
    assert response.status_code == 200
    body = response.json()
    assert body['agent'] == 'online'
    assert 0 <= body['health'] <= 100


def test_system_status_is_unified():
    response = client.get('/system/status')
    assert response.status_code == 200
    body = response.json()
    assert body['service']['name'] == 'X10THINK Sentinel'
    assert 'health' in body
    assert 'ai' in body
    assert isinstance(body['ai']['together_configured'], bool)


def test_dashboard_endpoint():
    response = client.get('/')
    assert response.status_code == 200
    assert 'X10THINK' in response.text


def test_unknown_action_is_rejected():
    response = client.post('/action?name=rm_everything')
    assert response.status_code == 400


def test_ai_without_keys_is_safe(monkeypatch):
    monkeypatch.delenv('TOGETHER_API_KEY', raising=False)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    from ai import analyze

    result = analyze({'score': 100})
    assert result['enabled'] is False
