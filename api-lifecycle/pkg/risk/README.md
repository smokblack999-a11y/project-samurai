# Risk engine contract

The risk engine is deterministic, explainable, and fail-closed.

Inputs:

- lifecycle status and sunset timestamp
- active consumer count
- observed traffic share
- unknown traffic share
- migration completion
- replacement health

Outputs:

- `SAFE` — no blocking evidence remains
- `REVIEW` — human/operator review is required
- `BLOCKED` — shutdown is unsafe under current evidence

Hard gates always override the numeric score:

1. endpoint must be explicitly marked `sunset`
2. sunset must have an explicit timestamp
3. active consumers must be zero
4. unknown traffic must be at or below the policy threshold
5. replacement, when supplied, must be healthy

`SAFE` is never inferred merely because the advertised Sunset time has arrived. RFC 8594 defines Sunset as a hint, not a guarantee.

The score is a prioritization signal, not permission to shut down an endpoint. AI may later explain evidence or propose migration work, but it must not replace the deterministic shutdown gate.
