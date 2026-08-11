from metrics import binary_metrics

def test_metrics_perfect():
    assert binary_metrics(10,0,0)=={"precision":1.0,"recall":1.0,"f1":1.0}

def test_metrics_zero_division():
    assert binary_metrics(0,0,0)=={"precision":0.0,"recall":0.0,"f1":0.0}
