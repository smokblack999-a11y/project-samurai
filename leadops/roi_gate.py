def roi_gate(estimated_revenue: float, monthly_price: float) -> bool:
    if estimated_revenue < 0 or monthly_price <= 0:
        return False
    return estimated_revenue / monthly_price >= 5.0
