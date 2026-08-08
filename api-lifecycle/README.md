# SAMURAI API Lifecycle Guard

API lifecycle control plane built around HTTP `Deprecation` and `Sunset` signals.

## Commercial wedge

The first sellable outcome is an **API Sunset Risk Audit**. A customer supplies an OpenAPI document and access-log evidence. SAMURAI returns an API inventory, consumer attribution, unknown-traffic analysis, migration readiness, and a SAFE/REVIEW/BLOCKED recommendation.

The recurring product is **API Lifecycle Guard**: continuously monitor API lifecycle state, consumer migration, RFC 8594 Sunset / RFC 9745 Deprecation signals, and shutdown readiness.

The product is sold on avoided outages and engineering time saved, not on the novelty of AI.

## Safety model

Sunset is a hint, not permission to shut down an API. The risk engine is fail-closed. Unknown traffic, active consumers, incomplete migration, or an unhealthy replacement keep an endpoint out of SAFE state.

AI may summarize evidence and propose migration actions. It must not override deterministic safety gates.

## Fast local demo

```bash
cd api-lifecycle
go test ./...
go vet ./...
go run ./cmd/samurai-lifecycle -input examples/decision-matrix.json
go run ./cmd/samurai-lifecycle -input examples/decision-matrix.json -json
```

## Initial commercial offers

- $500 fixed-price API Sunset Risk Audit.
- $1,500/month API Lifecycle Guard for continuous monitoring.
- $5,000+ enterprise API retirement program.

## Architecture

```text
OpenAPI / config
      |
      v
  API inventory -----> Lifecycle policy
      |                       |
      v                       v
Access logs ----------> Consumer attribution
                              |
                              v
                         Risk engine
                              |
                              v
                     SAFE / REVIEW / BLOCKED
                              |
                              v
                    Evidence / migration report
```

Production shutdown automation remains disabled by default.
