# Runbook

## Purpose
Query an existing evidence index file produced by Task Pack A.

## Commands
List runs:
- `PYTHONPATH=. python -m tools.evidence.cli list-runs --index .orchestrator_logs/evidence_index.json`

List artifacts for a run:
- `PYTHONPATH=. python -m tools.evidence.cli list-artifacts --index .orchestrator_logs/evidence_index.json --run-id <RUN_ID>`

Show a single artifact path:
- `PYTHONPATH=. python -m tools.evidence.cli show-artifact --index .orchestrator_logs/evidence_index.json --run-id <RUN_ID> --type <TYPE>`

Show index metadata:
- `PYTHONPATH=. python -m tools.evidence.cli show-index-meta --index .orchestrator_logs/evidence_index.json`

## Expected output
- Plain text, deterministic lines as specified in `tools.evidence.cli`.

## Troubleshooting
- Ensure the index file exists and contains `runs`.
- For ambiguous artifact queries, refine the requested type or pick a different run id.
