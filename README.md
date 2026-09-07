# SamuraiOS — RISC-V IOMMU Security Assurance Engine

Deterministic, evidence-first auditor for RISC-V Server SoC / IOMMU integration. The engine makes the security decision; an LLM is not used to decide whether a hardware requirement passes or fails.

The normative target is the ratified **RISC-V Server SoC v1.0** and the ratified **RISC-V IOMMU architecture release 20260222 (base architecture v1.0)**. These are distinct specifications and versions; SamuraiOS does not claim certification. Use the official RISC-V specifications for engineering/compliance decisions.

## Run

```bash
go test ./...
go run ./cmd/samurai audit target.json
go run ./cmd/samurai audit --format json target-bad.json
go run ./cmd/samurai audit --format sarif target-bad.json
go run ./cmd/samurai audit --format json --fail-on high target-bad.json
```

Exit code `1` means the selected severity gate was triggered. CI verifies this with an intentionally failing fixture.

## Current deterministic checks

The baseline covers:

- `IOM_010` — explicit negative evidence that an IOMMU does not support the required RISC-V IOMMU specification.
- `IOM_020` — DMA-capable peripherals and accessible PCIe root ports must be governed by an active IOMMU.
- `IOM_030` / `IOM_040` — Device ID width is checked according to whether an IOMMU governs a PCIe root port.
- `IOM_050` — modeled CPU page-based VM modes must be supported by the IOMMU when both evidence sets are present.
- `IOM_090` / `IOM_100` — ATS/T2GPA recommendations are advisory (`SHOULD`), not hard compliance failures.
- `IOM_110` — RCiEP ATS requirement (`MUST`).
- `IOM_130` — IOMMU MSI requirement (`MUST`).
- `IOM_170` — 20-bit PASID requirement when PASID is implemented (`MUST`).
- `IOM_230` — IOMMU physical address width must cover CPU physical address width.
- `IOM_240` — reset default must be `Off`.
- `IOM_260` — host bridge PMA/PMP enforcement for IOMMU-originated accesses.
- `IOM_270` — 24-bit Device IDs for multiple PCIe hierarchies.
- `IOM_280` / `IOM_290` / `IOM_300` / `IOM_310` — host-bridge integration checks are **evidence-gated**. Missing evidence is not converted into a fake failure; explicit negative evidence produces a finding.

Every finding carries severity, normative level, confidence, evidence, remediation and evidence provenance when supplied. `SARIF 2.1.0` output is available for CI/security tooling integration.

## Kill-critic boundary

This is an engineering MVP, not a certification claim. The commercial bottleneck is now clear: **replace hand-authored JSON with real platform evidence**.

Next sequence:

1. Linux Device Tree (`.dts` / `.dtb`) adapter.
2. IOMMU register/capability dump adapter.
3. Evidence provenance: source file, node/register/offset and extraction method.
4. Expand normative coverage only where the adapter can produce defensible evidence.
5. Reproducible fixtures from real or emulated RISC-V systems.
6. SARIF + CI security gate for SoC/vendor integration pipelines.
7. Optional OpenAI explanation/report layer after deterministic findings exist.

The product wedge is an **RISC-V IOMMU integration/security pre-audit and CI assurance tool** for SoC/IP/firmware teams. It is not positioned as a generic AI scanner or certification replacement.
