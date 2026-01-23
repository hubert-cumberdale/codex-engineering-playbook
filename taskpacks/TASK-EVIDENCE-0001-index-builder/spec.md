# Spec: Evidence Index Builder

## Objective
Provide a deterministic, offline, read-only evidence indexer that scans orchestrator logs and emits a stable, versioned `evidence_index.json`.

## Requirements
- Add `tools/evidence/` with `index.py`, `cli.py`, and `schemas.py`.
- The index output must include:
  - `schema_version` (integer, version 1)
  - `generated_at` (RFC3339 UTC)
  - `roots_scanned` (repo-relative roots scanned)
  - `runs` (deterministically ordered)
- Run entries must include `run_id`, `run_dir`, `manifest_path`, and `artifacts`.
- Artifact entries must include `type`, `path`, and `schema_version` when known.
- Deterministic rules only (no inference, no heuristics, no network, no AI/LLM usage).
- CLI entrypoint:
  - `python -m tools.evidence.cli index --root <path> --out <path>`
  - Defaults to `.orchestrator_logs` and `.orchestrator_logs/evidence_index.json`.
- Run discovery rule: a run is any directory under the scan root that directly contains `manifest.json`.
- Tests under `tools/evidence/tests/` cover ordering, schema version extraction, self-index ignore behavior, and the run discovery rule.

## Constraints
- No network access.
- No semantic inference or heuristic scanning.
- No new dependencies.
- No changes to orchestrator runtime behavior.
