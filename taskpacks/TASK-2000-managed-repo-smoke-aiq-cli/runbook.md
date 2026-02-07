# Runbook (Managed Repo Smoke)

## Preconditions
- Registry entry `aiq-cli` is present in `workspaces/registry.yml`.
- Target repo includes `docs/UX_MODEL.md` and `docs/GOVERNANCE.md`.
- No network access is required.

## How to run
```bash
TASKPACK_PATH=taskpacks/TASK-2000-managed-repo-smoke-aiq-cli \
ORCH_WORKSPACE=aiq-cli \
python tools/orchestrator/orchestrate.py
```

## Expected outputs
- Evidence in the managed workspace under `.orchestrator_logs/<run_id>/` (in-repo mode)
  or in the configured `evidence_dir` if `external_dir` is enabled.

## Acceptance verification
- `pytest` runs in the managed repo root.
- Changes (if any) are confined to `docs/`.
