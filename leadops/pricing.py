from dataclasses import dataclass

@dataclass(frozen=True)
class PilotEconomics:
    qualified_leads: int
    conversion_lift: float
    average_sale: float
    monthly_price: float

    def monthly_incremental_revenue(self) -> float:
        return round(self.qualified_leads * self.conversion_lift * self.average_sale, 2)

    def roi_multiple(self) -> float:
        return round(self.monthly_incremental_revenue() / self.monthly_price, 2) if self.monthly_price else 0.0
