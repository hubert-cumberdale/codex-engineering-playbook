# Runbook

## Purpose
Generate a deterministic evidence index for orchestrator logs.

## Command
- `PYTHONPATH=. python -m tools.evidence.cli index --root .orchestrator_logs --out .orchestrator_logs/evidence_index.json`

## Expected output
- A JSON file at the output path with schema version, timestamp, scanned roots, and deterministic run/artifact ordering.
- Run discovery only includes directories that directly contain `manifest.json`.

## Troubleshooting
- Ensure the root directory exists and contains `manifest.json` files in run directories.
- If the output is empty, verify the scan root points to the correct logs directory.
