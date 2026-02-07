# Runbook — TP-03 Intent (Stage-2)

## Preconditions
- Repository checked out locally.
- Python 3.10+ available.
- No hardware dependency; fixtures are deterministic.

## Stage-2 Validation (Deterministic, No Hardware)
From repository root:

```bash
python -m compileall -q solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/tools
python solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/tools/check_stage2_boundaries.py
python solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/tools/generate_stage2_artifacts.py
python solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/tools/check_stage2_artifacts.py
```

Expected artifacts:
- `solutions/game/fps-gaze-prototype/artifacts/stage-2/intent_resolution.log`
- `solutions/game/fps-gaze-prototype/artifacts/stage-2/intent_report.json`

## Task Pack Acceptance Commands

```bash
python tools/acceptance/check_git_diff_scope.py --allowed solutions/game/fps-gaze-prototype
python tools/acceptance/check_no_qualitative_language.py --path solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent
python tools/acceptance/check_artifacts_present.py --path solutions/game/fps-gaze-prototype/artifacts/stage-2
python tools/acceptance/check_artifact_contains_any.py --path solutions/game/fps-gaze-prototype/artifacts/stage-2 --any deterministic tie_break null_intent stage-2
python tools/acceptance/check_engine_declared_in_taskpack.py --task-yml solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/task.yml --spec solutions/game/fps-gaze-prototype/taskpacks/tp-03-intent/design.md --artifact-path solutions/game/fps-gaze-prototype/artifacts/stage-2
```

## Notes
- Stage-2 excludes adapters and gameplay side effects.
- Artifacts must not include raw gaze stream arrays.
- Log output is scenario-level only (no repeated coordinate dumps).
