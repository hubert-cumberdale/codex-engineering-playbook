# Spec: Review Allowlist Update (Orchestrator)

## Objective
Allow deterministic review to accept changes under `tools/orchestrator/orchestrate.py` by adding an explicit allowlist entry, without altering any other review behavior.

## Requirements
- Add a single allowlist entry for `tools/orchestrator/orchestrate.py`.
- Add tests that lock the allowlist entry and verify `check_scope` passes for that path.

## Constraints
- No behavior changes beyond allowlist inclusion.
- No new dependencies.
