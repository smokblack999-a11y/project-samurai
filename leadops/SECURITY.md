# LeadOps security boundary

- Never commit `OPENAI_API_KEY`, Telegram session files, bot tokens, or `.env` files.
- Do not log full Telegram message bodies in production.
- TDLib credentials remain outside the AI layer.
- Store only the minimum fields required for deduplication, evaluation, and business reporting.
- Outbound Telegram automation stays disabled during validation.
- Real evaluation data must be anonymized, consented, or otherwise authorized.
- Human review is required for high-value actions.
