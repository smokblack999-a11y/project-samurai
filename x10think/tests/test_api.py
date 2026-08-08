from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_status_endpoint():
    response = client.get('/status')
    assert response.status_code == 200
    body = response.json()
    assert body['agent'] == 'online'
    assert 0 <= body['health'] <= 100


def test_dashboard_endpoint():
    response = client.get('/')
    assert response.status_code == 200
    assert 'X10THINK' in response.text
