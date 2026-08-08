# Risk engine contract

The first risk engine must be deterministic and explainable. Do not use an LLM for the core decision.

Inputs:

- traffic share
- unknown traffic share
- active consumer count
- migration completion
- replacement health
- time until sunset

Outputs:

- `SAFE`
- `REVIEW`
- `BLOCKED`

A `SAFE` result must include evidence and thresholds. The system must never infer that an API is safe to disable solely because its advertised Sunset date has arrived; RFC 8594 treats Sunset as a hint rather than a guarantee.

Later versions can add adapters for gateway/APM/log sources and an AI explanation layer, but the underlying decision remains reproducible.
