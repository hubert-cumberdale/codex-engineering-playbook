# Spec: Orchestrator Evidence Index Write (Opt-In)

## Objective
Add an opt-in orchestrator integration to write an evidence index after a run completes, without changing defaults or adding enforcement.

## Requirements
- Add env flag `ORCH_WRITE_EVIDENCE_INDEX=1` to enable index writing.
- When enabled, build the evidence index from `.orchestrator_logs/` and write `.orchestrator_logs/evidence_index.json`.
- Record `evidence_index_path` and `evidence_index_schema_version` in the manifest.
- On failure, do not fail the run; record `evidence_index_error` in the manifest.
- Default behavior unchanged when env flag is unset.

## Example command (local)
- `ORCH_WRITE_EVIDENCE_INDEX=1 TASKPACK_PATH=taskpacks/TASK-REVIEW-0001-deterministic-review-runner python tools/orchestrator/orchestrate.py`

## Constraints
- No network access.
- Deterministic, auditable behavior only.
- No new dependencies.
- No enforcement or gating based on evidence contents.
