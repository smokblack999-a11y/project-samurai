package monetization

// Offer is deliberately sales-oriented: sell a risk review and migration
// readiness outcome, not generic "AI" or a dashboard.
type Offer struct {
    Name        string   `json:"name"`
    PriceUSD    int      `json:"price_usd"`
    Deliverables []string `json:"deliverables"`
}

var Offers = []Offer{
    {
        Name: "API Sunset Risk Audit",
        PriceUSD: 500,
        Deliverables: []string{
            "API inventory and deprecated-version map",
            "consumer attribution from access logs",
            "unknown-traffic and active-consumer evidence",
            "SAFE/REVIEW/BLOCKED shutdown report",
            "migration action list",
        },
    },
    {
        Name: "API Lifecycle Guard",
        PriceUSD: 1500,
        Deliverables: []string{
            "continuous lifecycle monitoring",
            "RFC Sunset/Deprecation header checks",
            "consumer migration tracking",
            "risk alerts and evidence reports",
        },
    },
    {
        Name: "Enterprise API Retirement Program",
        PriceUSD: 5000,
        Deliverables: []string{
            "multi-service API inventory",
            "custom policy and evidence retention",
            "migration readiness reviews",
            "deployment/shutdown approval workflow",
        },
    },
}
