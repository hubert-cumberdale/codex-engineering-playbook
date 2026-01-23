# Runbook

## Purpose
Enable evidence index writing after orchestrator runs.

## Command
- `ORCH_WRITE_EVIDENCE_INDEX=1 TASKPACK_PATH=taskpacks/TASK-REVIEW-0001-deterministic-review-runner python tools/orchestrator/orchestrate.py`

## Expected output
- `.orchestrator_logs/evidence_index.json` is written when enabled.
- Manifest includes `evidence_index_path` and `evidence_index_schema_version`.

## Troubleshooting
- If the index is missing, confirm `ORCH_WRITE_EVIDENCE_INDEX=1` is set.
- Check manifest for `evidence_index_error` when indexing fails.
