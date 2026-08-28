from dataclasses import dataclass

@dataclass(frozen=True)
class UnitEconomics:
    monthly_price_usd: float
    analyses_per_month: int
    ai_cost_per_analysis_usd: float
    fixed_monthly_cost_usd: float = 0.0

    @property
    def ai_cost(self) -> float:
        return self.analyses_per_month * self.ai_cost_per_analysis_usd

    @property
    def gross_margin_usd(self) -> float:
        return self.monthly_price_usd - self.ai_cost - self.fixed_monthly_cost_usd

    @property
    def gross_margin_pct(self) -> float:
        if self.monthly_price_usd <= 0:
            return 0.0
        return self.gross_margin_usd / self.monthly_price_usd
