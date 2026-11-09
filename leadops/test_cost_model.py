from cost_model import UnitEconomics

def test_positive_margin():
    x = UnitEconomics(monthly_price_usd=49, analyses_per_month=10000, ai_cost_per_analysis_usd=0.001)
    assert x.gross_margin_usd > 0
    assert 0 < x.gross_margin_pct < 1

def test_zero_price_is_safe():
    x = UnitEconomics(monthly_price_usd=0, analyses_per_month=1, ai_cost_per_analysis_usd=0.001)
    assert x.gross_margin_pct == 0
