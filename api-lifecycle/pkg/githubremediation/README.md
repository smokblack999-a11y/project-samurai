# GitHub remediation loop

This package converts deterministic API lifecycle evidence into a GitHub-ready remediation payload.

## Contract

`BLOCKED` and `REVIEW` produce actionable issue content. `SAFE` remains a successful audit result and must not create a remediation issue.

The fingerprint is deterministic over endpoint identity, decision, score, confidence, consumers, and reasons. Consumers and reasons are sorted before hashing, so input ordering does not change deduplication.

The payload is intentionally side-effect free. A separate integration layer should own GitHub write access, idempotency lookup, and issue state transitions.

## Why this exists

API retirement is safe only when the provider has evidence about active consumers and a tested migration path. RFC 8594 defines `Sunset` as a hint about expected future unavailability, not a guarantee. GitHub itself uses `Sunset` and `Deprecation` headers when API versions approach closure.

The product therefore treats lifecycle evidence as the source of truth and uses GitHub as the remediation control plane.
