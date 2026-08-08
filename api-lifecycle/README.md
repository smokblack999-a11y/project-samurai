# SAMURAI API Lifecycle

API lifecycle control plane MVP built around HTTP `Deprecation` and `Sunset` signals.

## Goal

Answer one operational question:

> Which APIs can we safely sunset, who still uses them, and what blocks migration?

The MVP deliberately starts below the enterprise control-plane layer:

- OpenAPI inventory
- lifecycle metadata (`active`, `deprecated`, `sunset`)
- RFC-aware response headers
- consumer observations
- deterministic risk scoring
- `safe-to-sunset` decision output

## Design

```text
OpenAPI / config
      |
      v
  API inventory -----> Lifecycle policy
      |                       |
      v                       v
Consumer observations --> Risk engine
                              |
                              v
                       SAFE / BLOCKED
```

## Repository roadmap

1. `schema/` — stable lifecycle data model.
2. `cmd/` — CLI scanner/reporting.
3. `pkg/headers/` — RFC 8594/RFC 9745 header generation/parsing.
4. `pkg/risk/` — explainable risk score.
5. `examples/` — sample API inventory and consumer data.
6. GitHub Actions — CI and later policy checks on OpenAPI changes.

## Product boundary

This is not another middleware-only package. Headers are the interoperability layer; consumer intelligence and safe-shutdown decisions are the product layer.

## Status

MVP scaffold. No production shutdown automation is enabled by default.
