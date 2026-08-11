# LeadOps security boundary

- Never commit API keys or session files.
- Do not log full Telegram message bodies in production.
- TDLib credentials remain outside the AI layer.
- Outbound Telegram automation stays disabled during the validation phase.
- Use anonymized datasets for evaluation.
- Human review is required for high-value actions.
