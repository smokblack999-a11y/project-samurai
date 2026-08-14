# AI Margin Audit

A zero-integration forensic audit for AI-native SaaS teams.

## Commercial wedge

Do not sell another generic LLM dashboard. Sell a fixed-scope audit that answers three questions:

1. Where is AI spend actually coming from?
2. Which workloads are economically dangerous or inefficient?
3. What concrete engineering/FinOps changes should be made first?

The first offer is service-led, not SaaS-led. A customer can provide an OpenAI/Anthropic usage export or normalized CSV. The tool produces evidence-backed findings. No fabricated savings percentages are shown.

## MVP input

CSV columns supported by `audit.py`:

- timestamp
- provider
- model
- input_tokens
- output_tokens
- cost_usd
- feature (optional)
- customer (optional)

## Output

- total spend
- spend by provider/model/feature/customer when available
- concentration risk
- high-cost rows
- missing attribution fields
- deterministic recommendations

## Important limitation

This tool does not claim savings before customer data is analyzed. Estimated savings must be based on measured baseline data and clearly labeled assumptions.

## Suggested initial offer

- Diagnostic audit: $99-$299
- Implementation sprint: $500-$2,000 depending on scope
- Recurring monitoring/optimization: $299-$799/month only after a real baseline exists

These are proposed test prices, not market facts or guaranteed conversion rates.
