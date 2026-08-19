# SAMURAI SENTINEL X

Defensive security orchestration layer combining Wazuh, Tetragon and osquery/YARA into one normalized incident pipeline.

## Architecture

```text
Wazuh ───────┐
Tetragon ────┼──> Normalizer ──> Correlator ──> Risk Engine ──> Incident Graph/API
osquery/YARA ┘                                      │
                                                    └──> Response Planner
```

## MVP scope

- Normalized event schema with source provenance.
- Deterministic correlation of process/file/network/persistence signals.
- Explainable 0-100 risk score.
- Incident timeline and evidence graph.
- Read-only adapters first; response actions remain explicit and audited.
- No offensive capability, exploit delivery, credential theft, or persistence tooling.

## Real integrations

Wazuh exposes a REST API for manager/agent management and telemetry queries. Tetragon supplies eBPF runtime security events. osquery supplies SQL-based endpoint inventory/telemetry; YARA is used as a detection engine.

The adapters in this repository intentionally accept normalized JSON so the core can be tested without requiring a live security stack.

## Run

```bash
cd sentinel-x
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8787
```

Then open `GET /health`, `POST /events`, `GET /incidents` and `GET /incidents/{id}`.

## Security rule

This project is for authorized defensive monitoring and incident response. Keep response integrations disabled until the target environment, permissions and rollback procedure are explicitly verified.
