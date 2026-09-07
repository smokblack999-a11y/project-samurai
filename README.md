# SamuraiOS — RISC-V IOMMU Security Assurance Engine

Deterministic, evidence-first auditor for RISC-V Server SoC / IOMMU integration. The engine makes the security decision; an LLM is not used to decide whether a hardware requirement passes or fails.

The current normative target is the ratified RISC-V Server SoC Requirements v1.0 and the ratified RISC-V IOMMU architecture v1.0.1. The IOMMU architecture release is 20260222. See the official RISC-V specifications before using results for engineering or compliance decisions.

## Run

```bash
go test ./...
go run ./cmd/samurai audit target.json
go run ./cmd/samurai audit --format json target-bad.json
go run ./cmd/samurai audit --format sarif target-bad.json
go run ./cmd/samurai audit --format json --fail-on high target-bad.json
```

Exit code `1` means the selected severity gate was triggered. The CI workflow verifies this behavior instead of hiding an intentionally failing fixture behind `continue-on-error`.

## Current deterministic checks

The current baseline covers:

- `IOM_020` — DMA-capable peripherals and accessible PCIe root ports must be governed by an active IOMMU.
- `IOM_030` / `IOM_040` — Device ID width is checked according to whether an IOMMU governs a PCIe root port.
- `IOM_090` / `IOM_100` — ATS/T2GPA recommendations are advisory (`SHOULD`), not hard compliance failures.
- `IOM_110` — RCiEP ATS requirement (`MUST`).
- `IOM_130` — IOMMU MSI requirement (`MUST`).
- `IOM_170` — 20-bit PASID requirement when PASID is implemented (`MUST`).
- `IOM_230` — IOMMU physical address width must cover the CPU physical address width.
- `IOM_240` — reset default must be `Off`.
- `IOM_260` — host bridge PMA/PMP enforcement for IOMMU-originated accesses.
- `IOM_270` — 24-bit Device IDs for multiple PCIe hierarchies.

Every finding carries severity, normative level, confidence, rule ID, evidence and remediation. `SARIF 2.1.0` output is available for CI/security tooling integration.

## Kill-critic boundary

This is an engineering MVP, not a certification claim. The biggest missing commercial capability is **real evidence ingestion**. The next implementation step is to ingest actual platform evidence rather than hand-authored JSON:

1. Linux Device Tree (`.dts` / `.dtb`) adapter.
2. IOMMU register/capability dump adapter.
3. Normalized evidence model with source locations and provenance.
4. More normative rules, especially `IOM_010`, `IOM_050`, `IOM_280`, `IOM_290`, `IOM_300`, and `IOM_310`.
5. Reproducible fixtures from real or emulated RISC-V systems.
6. CI gate + SARIF for vendor/SoC integration pipelines.
7. Optional OpenAI explanation/report layer after deterministic findings exist.

The product should be sold as an **IOMMU integration/security pre-audit and CI assurance tool**, not as a generic AI security scanner and not as a certification replacement.
