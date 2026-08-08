# SAMURAI API Lifecycle Core

The core answers one operational question: **can this API be safely sunset?**

The decision path is deterministic:

1. Validate lifecycle evidence.
2. Calculate risk from explicit, versioned thresholds.
3. Return `SAFE`, `REVIEW`, or `BLOCKED`.
4. Return machine-readable reasons and evidence.

AI is intentionally outside the critical decision path. It can later explain evidence or propose migrations, but it must not silently override the safety decision.

## Current hard blockers

- Any active consumer blocks shutdown.
- Migration completion below 100% blocks shutdown.

## Risk signals

- High traffic share: >= 20%.
- High unknown traffic share: >= 10%.
- Unhealthy replacement when a replacement is declared.

## CLI

```bash
go test ./...
go run ./cmd/samurai-lifecycle -input examples/sample-lifecycle.json
```

The sample should produce `BLOCKED`, because it has five active consumers and only 42% migration completion.
