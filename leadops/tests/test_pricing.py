from pricing import PilotEconomics


def test_pricing_math():
    economics = PilotEconomics(100, 0.10, 200, 149)
    assert economics.monthly_incremental_revenue() == 2000.0
    assert economics.roi_multiple() == 13.42
