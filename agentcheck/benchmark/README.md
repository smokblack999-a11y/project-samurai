# AgentCheck benchmark

Purpose: measure whether findings are reproducible and useful, not merely numerous.

## Evidence lifecycle

`candidate -> reproduced -> confirmed -> remediated -> verified -> regression_safe`

A finding is not treated as a confirmed vulnerability until evidence supports it. Static heuristics alone remain candidates.

## Metrics

- precision = confirmed / manually reviewed findings
- false-positive rate = false_positive / manually reviewed findings
- reproduction rate = reproduced / candidates
- fix rate = verified / confirmed
- regression rate = regression failures / verified remediations

## Benchmark rules

1. Pin the target repository and commit.
2. Record exact rule IDs and evidence locations.
3. Never count an unverified heuristic as a confirmed vulnerability.
4. Separate scanner output from manual adjudication.
5. Use only authorized, local, or intentionally vulnerable targets for dynamic verification.

## Commercial gate

Do not market a security guarantee from benchmark results. The benchmark is evidence for product quality and for a scoped audit service.

Initial gate: >=80% precision on a manually reviewed sample, plus at least one finding that leads to a concrete remediation and successful re-test.
