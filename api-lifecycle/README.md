# SAMURAI API Lifecycle

API lifecycle control plane MVP built around HTTP `Deprecation` and `Sunset` signals.

## Goal

Answer one operational question:

> Which APIs can we safely sunset, who still uses them, and what blocks migration?

The current Go core is intentionally deterministic: OpenAPI JSON -> inventory -> lifecycle model -> risk engine -> terminal report. No LLM is placed in the safety decision path.

## Run

```bash
cd api-lifecycle
go test ./...
go vet ./...
go run ./cmd/samurai-lifecycle -openapi examples/openapi.json
```

## Decision model

- `SAFE`: no blocking evidence for shutdown.
- `REVIEW`: evidence exists and migration state needs verification.
- `BLOCKED`: active consumers, material traffic, unknown traffic, incomplete migration, or unhealthy replacement create shutdown risk.

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
                     SAFE / REVIEW / BLOCKED
```

## Roadmap

1. Stable lifecycle schema.
2. Go risk engine and tests.
3. OpenAPI inventory scanner.
4. RFC 8594/RFC 9745 header adapters.
5. Access-log and gateway consumer attribution.
6. Migration diffing and policy-as-code.
7. GitHub Action annotations and dashboard.
8. Enterprise control plane with auditable safe-shutdown evidence.

Headers are the interoperability layer; consumer intelligence and safe-shutdown decisions are the product layer.

Production shutdown automation remains disabled by default.
