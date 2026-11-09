# Telegram LeadOps AI

## ICP
Small and midsize businesses that receive sales/support requests through Telegram and lose opportunities because messages are not prioritized or acted on quickly.

## Core outcome
Turn incoming Telegram messages into prioritized leads and concrete next actions.

## MVP flow
Telegram/TDLib -> event normalization -> AI decision engine -> persistence -> dashboard/API.

## Decision schema
- intent: buying | support | information | spam | other
- lead_score: 0..100
- urgency: low | medium | high
- recommended_action: auto_reply | human_followup | ignore | escalate
- needs: string[]
- reason: string

## Commercial validation
Do not scale features until at least one real pilot is willing to pay. Target: 10 prospects -> 5 demos -> 3 pilots -> 1 paid pilot.

## Kill criteria
If prospects do not understand the value within 30 seconds, narrow the ICP or rewrite the offer. Do not compensate with more features.
