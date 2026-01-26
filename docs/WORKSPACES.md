# Managed Workspaces

This document describes how the orchestrator targets external repositories by
registry name or local path and where evidence is written.

This is usage guidance (Tier-2). Authoritative system behavior remains in `/docs`.

---

## Registry format

The workspace registry lives at `workspaces/registry.yml`.

```yaml
version: 1

defaults:
  kind: local_path
  evidence_mode: in_repo
  acceptance:
    - python -m pytest -q

workspaces:
  aiq-cli:
    kind: local_path
    path: /abs/path/to/aiq-cli
    evidence_mode: in_repo
    acceptance:
      - python -m pytest -q
```

Rules:
- `kind` is `local_path` (no cloning yet).
- `path` must be absolute.
- `evidence_mode` is `in_repo` or `external_dir`.
- `evidence_dir` is required when `evidence_mode=external_dir`.
- Registry must not contain secrets.

---

## Workspace resolution precedence

The orchestrator resolves the workspace in this order:
1) CLI flag `--workspace <name_or_path>`
2) Environment variable `ORCH_WORKSPACE`
3) `task.yml: workspace`

If none are set, the orchestrator fails fast with:
“No workspace specified. Provide --workspace <name|path> or workspace: in task.yml (or workspace: playbook for self).”

If the value matches a registry name, that workspace entry is used.
Otherwise the value is treated as a local path.

To intentionally target the playbook repo, set `workspace: playbook` (or `workspace: self`)
in `task.yml` or pass the same value via CLI or env.

---

## Evidence routing

Evidence is written per run (`<run_id>`):

- `in_repo`:
  - `<workspace_root>/.orchestrator_logs/<run_id>/...`

- `external_dir`:
  - `<evidence_dir>/<run_id>/...`

Managed repo evidence is never written inside the playbook repo.

---

## Examples

Run a managed workspace by registry name:
```bash
TASKPACK_PATH=taskpacks/TASK-2000-managed-repo-smoke-aiq-cli \
ORCH_WORKSPACE=aiq-cli \
python tools/orchestrator/orchestrate.py
```

Run by path (no registry entry):
```bash
TASKPACK_PATH=taskpacks/TASK-2000-managed-repo-smoke-aiq-cli \
ORCH_WORKSPACE=/abs/path/to/aiq-cli \
python tools/orchestrator/orchestrate.py
```

`workspace: playbook` targets the orchestrator repository itself (use sparingly; prefer explicit external workspaces for managed repos).
