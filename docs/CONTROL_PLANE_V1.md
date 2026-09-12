# SAMURAI CONTROL PLANE v1

## Product

A control and verification layer for autonomous AI agents. Agents do not receive unrestricted authority. Every meaningful tool action is represented as an ActionEnvelope and evaluated by deterministic policy before execution.

## v1 trust loop

```text
AGENT
  -> ACTION ENVELOPE
  -> POLICY ENGINE
  -> ALLOW / REVIEW / BLOCK
  -> EXECUTION (future adapter)
  -> RESULT (future verifier)
  -> AUDIT LEDGER
  -> TRUST ENGINE
```

## 15-step execution roadmap

1. Agent identity: stable ID, version, owner and declared tools.
2. Action envelope: one canonical representation for every tool call.
3. Evidence contract: source, fact, observation time and confidence.
4. Deterministic policy gate: hard blocks cannot be overridden by an LLM.
5. Permission tiers: READ, DRAFT, APPROVAL, AUTONOMOUS.
6. Kill Critic: combine hard policy with risk/evidence checks before execution.
7. Sandbox adapter: execute untrusted code outside the production control plane.
8. GitHub adapter: PR -> CI -> diagnosis -> patch -> test -> verification.
9. Result verifier: require machine-checkable success conditions.
10. Append-only audit: record action, decision, evidence and result.
11. Trust engine: update agent trust from measured outcomes, rollback and incidents.
12. Cost brain: measure model/tool/runtime spend per successful action.
13. Model router: select frontier or local inference by quality, latency and cost.
14. Red-team harness: test prompt injection, tool abuse, secret leakage and privilege escalation.
15. Commercial wedge: ship GitHub Agent Gate first, then expand to enterprise tools.

## Non-negotiable rules

- No fabricated evidence.
- No 98% success claims without measured evaluation data.
- LLMs cannot override deterministic hard blocks.
- Production mutations default to approval until verified safe.
- Secrets never enter the audit payload.
- Every autonomous action must be replayable and attributable.
- Local JSONL is an MVP ledger only; production persistence moves behind PostgreSQL.
