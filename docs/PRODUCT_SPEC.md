# Telegram LeadOps AI — Product Spec

## Outcome
Turn Telegram conversations into ranked business opportunities and explicit next actions.

## ICP
Small and midsize service businesses that receive customer inquiries through Telegram and lose revenue because messages are not prioritized or followed up quickly.

## Core job
For each incoming message, determine intent, urgency, lead score, needs, and recommended human action.

## MVP flow
Telegram/TDLib -> event normalizer -> FastAPI -> AI decision engine -> persistence -> dashboard/API.

## Canonical decision
```json
{
  "intent": "buying|question|support|spam|other",
  "lead_score": 0,
  "urgency": "low|medium|high",
  "language": "string",
  "needs": ["string"],
  "recommended_action": "human_followup|reply|ignore|escalate",
  "reason": "string"
}
```

## Success metrics
- classification accuracy >= 90% on the controlled evaluation set;
- no secret leakage in repository or logs;
- API health check < 500 ms without model call;
- every AI decision has a persisted event ID;
- pilot user can identify the highest-priority leads in under 30 seconds.

## Kill criteria
If 10 qualified prospects produce zero pilot interest, stop feature expansion and revisit ICP/value proposition before adding infrastructure.

## Commercial hypothesis
Start with a free diagnostic/pilot, then test $19/$49/$149 monthly tiers based on message volume and operational features. Pricing is a hypothesis and must be validated by paid pilots.

## Non-goals
No custom LLM, no large CRM, no autonomous outbound messaging, no Kubernetes, no mobile app, no complex 3D UI in MVP.
