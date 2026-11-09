from roi_gate import roi_gate

def test_five_x_gate():
    assert roi_gate(750, 149) is True

def test_weak_roi_fails():
    assert roi_gate(500, 149) is False

def test_invalid_price_fails():
    assert roi_gate(1000, 0) is False
