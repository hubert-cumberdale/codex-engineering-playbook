# Runbook

## Purpose
Confirm deterministic review allows changes to the orchestrator entrypoint path.

## Command
- `PYTHONPATH=. python -m pytest -q`

## Expected output
- Tests pass and the orchestrator path is present in the allowlist.
