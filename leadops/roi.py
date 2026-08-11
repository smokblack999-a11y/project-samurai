from dataclasses import dataclass

@dataclass(frozen=True)
class BusinessInput:
    monthly_messages: int
    hot_leads: int
    conversion_rate: float
    average_sale: float
    software_price: float

def calculate(i: BusinessInput) -> dict:
    customers = i.hot_leads * i.conversion_rate
    revenue = customers * i.average_sale
    return {
        "estimated_customers": round(customers, 2),
        "estimated_revenue": round(revenue, 2),
        "software_cost": round(i.software_price, 2),
        "roi_multiplier": round(revenue / i.software_price, 2) if i.software_price else 0,
        "net_estimated_value": round(revenue - i.software_price, 2),
    }
