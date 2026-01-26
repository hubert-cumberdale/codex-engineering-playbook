# Evidence Index

## Overview
The evidence index is a deterministic, read-only JSON inventory of orchestrator evidence.
It is produced offline by `tools.evidence` and does not scan or interpret evidence at query time.

What it is:
- A stable index of runs and artifacts under `.orchestrator_logs` (or an external evidence root).
- Deterministic and auditable output based on explicit file matches.

What it is not:
- Enforcement or scoring.
- A source of live or derived data.

## Generate the index
Use the index builder from Task Pack A:
- `PYTHONPATH=. python -m tools.evidence.cli index --root .orchestrator_logs --out .orchestrator_logs/evidence_index.json`
- For external evidence roots:
  `PYTHONPATH=. python -m tools.evidence.cli index --root <evidence_dir> --out <evidence_dir>/evidence_index.json`

## Query the index
All query commands read the index file only and never rescan the filesystem.

List runs:
- `PYTHONPATH=. python -m tools.evidence.cli list-runs --index .orchestrator_logs/evidence_index.json`
- External mode: `PYTHONPATH=. python -m tools.evidence.cli list-runs --index <evidence_dir>/evidence_index.json`

List artifacts for a run:
- `PYTHONPATH=. python -m tools.evidence.cli list-artifacts --index .orchestrator_logs/evidence_index.json --run-id <RUN_ID>`
- External mode: `PYTHONPATH=. python -m tools.evidence.cli list-artifacts --index <evidence_dir>/evidence_index.json --run-id <RUN_ID>`

Show a single artifact path:
- `PYTHONPATH=. python -m tools.evidence.cli show-artifact --index .orchestrator_logs/evidence_index.json --run-id <RUN_ID> --type <TYPE>`
- External mode: `PYTHONPATH=. python -m tools.evidence.cli show-artifact --index <evidence_dir>/evidence_index.json --run-id <RUN_ID> --type <TYPE>`

Show index metadata:
- `PYTHONPATH=. python -m tools.evidence.cli show-index-meta --index .orchestrator_logs/evidence_index.json`
- External mode: `PYTHONPATH=. python -m tools.evidence.cli show-index-meta --index <evidence_dir>/evidence_index.json`

## Schema overview (v1)
Top-level fields:
- `schema_version`: integer (current: 1)
- `generated_at`: RFC3339 UTC timestamp
- `roots_scanned`: list of repo-relative roots
- `runs`: array of run entries

Run entry fields:
- `run_id`
- `run_dir`
- `manifest_path`
- `artifacts`

Artifact entry fields:
- `type`
- `path`
- `schema_version` (null when unknown or unreadable)

Schema version statement:
- Evidence index schema version is `1`.
