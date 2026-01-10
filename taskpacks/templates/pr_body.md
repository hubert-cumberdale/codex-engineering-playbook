## Summary
Wire v2 solution plugins into `tools/orchestrator/orchestrate.py` behind a flag and execute them via the v2 plugin runner.

## What changed
- Add `ORCH_ENABLE_PLUGINS=1` / `--enable-plugins` to run the plugin declared in `task.yml` (`plugin:`).
- Create and pass an `ExecutionContext` (`run_id`, `workspace_dir`, `artifact_dir`, `constraints`) into the v2 plugin runner.
- Record plugin execution status and result path in `.orchestrator_logs/manifest.json`.
- Normalize plugin artifact paths in `plugin_result.json` (relative paths for portability).
- Ensure CI pushes use HTTPS token auth when running under GitHub Actions.
- Add `ORCH_BRANCH_NAME` support and a PR-exists guard to prevent branch/PR spam.

## How to run
```bash
ORCH_BRANCH_NAME=codex/task-0102 \
TASKPACK_PATH=taskpacks/TASK-0102-orchestrator-plugin-arch \
ORCH_ENABLE_PLUGINS=1 \
RUN_CODEX_SMOKE=false \
python tools/orchestrator/orchestrate.py
```

## Evidence
- `python -m pytest -q`
- Plugin artifacts created under `.orchestrator_logs/plugin/TASK-0102/`:
    - `echo.txt`
    - `echo_report.md`
    - `plugin_result.json`

## Risk / rollback
- Risk:
    - <…>
- Rollback:
    - Revert commit(s) / disable flag(s): `<flags or files>`

## Checklist
- [X] Tests pass
- [X] Acceptance criteria met
- [X] No secrets introduced
- [ ] Safety constraints honored (network/cloud mutations)
- [ ] Logs/artifacts produced for auditability