import pytest
from app import auth
from app.main import add_outbox
from app.models import Outbox

class FakeSession:
    def __init__(self):
        self.items=[]
    def add(self,item):
        self.items.append(item)

def test_websocket_token_round_trip(monkeypatch):
    monkeypatch.setattr(auth.settings,'WS_TOKEN_SECRET','unit-test-secret',raising=False)
    token=auth.issue_ws_token('project-a',ttl_seconds=60)
    assert auth.verify_ws_token(token,'project-a')
    assert not auth.verify_ws_token(token,'project-b')

def test_websocket_token_rejects_tampering(monkeypatch):
    monkeypatch.setattr(auth.settings,'WS_TOKEN_SECRET','unit-test-secret',raising=False)
    token=auth.issue_ws_token('project-a')
    tampered=token[:-1]+('0' if token[-1]!='0' else '1')
    assert not auth.verify_ws_token(tampered,'project-a')

def test_outbox_record_contains_routable_event():
    session=FakeSession()
    add_outbox(session,'evt_1','project-a','invoice.created',{'invoice_id':'inv_1'})
    assert len(session.items)==1
    row=session.items[0]
    assert isinstance(row,Outbox)
    assert row.event_id=='evt_1'
    assert row.payload=={
        'id':'evt_1',
        'project_id':'project-a',
        'type':'invoice.created',
        'payload':{'invoice_id':'inv_1'},
    }
