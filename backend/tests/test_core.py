import sys
sys.path.insert(0,'.')
from fastapi.testclient import TestClient
from main import app
from core.schemas import Receipt,ReceiptItem
from core.validation import validate_receipt
from domain.economics import margin_percent,profit_minor

def test_health(): assert TestClient(app).get('/health').json()['ok'] is True

def test_validation():
    r=Receipt(merchant='x',items=[ReceiptItem(name='milk',quantity=2,unit_price=500,line_total=1000,confidence=.9)],total=1000,confidence=.9)
    assert validate_receipt(r).valid

def test_economics():
    assert margin_percent(700,1000)==30.0
    assert profit_minor(700,1000,3)==900
