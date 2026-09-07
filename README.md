# SamuraiOS — RISC-V IOMMU Security Assurance Engine

Deterministic first-pass auditor for RISC-V Server SoC / IOMMU integration. It is evidence-first: no LLM decides whether a hardware requirement passes or fails.

## Run

```bash
go test ./...
go run ./cmd/samurai audit target.json
go run ./cmd/samurai audit --format json target-bad.json
go run ./cmd/samurai audit --format json --fail-on high target-bad.json
```

## Current checks

The first implementation covers deterministic checks derived from RISC-V Server SoC requirements, including IOM_020, IOM_040, IOM_090, IOM_100, IOM_110, IOM_130, IOM_160, IOM_230, IOM_240, IOM_260 and IOM_270.

These are an implementation baseline, not a certification claim. Each rule must be expanded with exact evidence adapters for real DTS, register dumps, RTL/simulation output and platform-specific configuration before commercial compliance use.

## Product direction

Input adapters → normalized SoC/IOMMU model → deterministic rules → evidence/severity → JSON/SARIF/CI. OpenAI can later explain findings and generate customer reports, but it must not replace the deterministic decision engine.
