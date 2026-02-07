# Runbook — TP-02 Provider (Stage-1)

## Preconditions
- Repository checked out locally.
- Python 3.10+ available.
- Unreal Engine 4.27 optional for runtime command verification.

## Deterministic Stage-1 Validation (No Hardware Required)
From repository root:

```bash
python -m compileall -q solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/tools
python solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/tools/check_stage1_boundaries.py
python solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/tools/generate_stage1_artifacts.py
python solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/tools/check_stage1_artifacts.py
```

Expected artifacts:
- `solutions/game/fps-gaze-prototype/artifacts/stage-1/signal_contract.md`
- `solutions/game/fps-gaze-prototype/artifacts/stage-1/runtime_validation.log`
- `solutions/game/fps-gaze-prototype/artifacts/stage-1/provider_status.json`

## Task Pack Acceptance Commands

```bash
python tools/acceptance/check_git_diff_scope.py --allowed solutions/game/fps-gaze-prototype
python tools/acceptance/check_no_qualitative_language.py --path solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider
python tools/acceptance/check_artifacts_present.py --path solutions/game/fps-gaze-prototype/artifacts/stage-1
python tools/acceptance/check_artifact_contains_any.py --path solutions/game/fps-gaze-prototype/artifacts/stage-1 --any schema_version threshold monotonic deterministic
python tools/acceptance/check_engine_declared_in_taskpack.py --task-yml solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/task.yml --spec solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/design.md --artifact-path solutions/game/fps-gaze-prototype/artifacts/stage-1
```

## Optional Unreal Runtime Validation
When the Unreal project is opened and running:
1. Confirm `Config/DefaultGame.ini` contains `Gaze.Enabled` and `Gaze.Provider`.
2. Run console command `Gaze.Toggle` and verify provider enabled state changes.
3. Run console command `Gaze.ValidateStage1` to write Stage-1 artifacts.
4. Compare artifacts with deterministic contract fields and keys.

## Local Verification (Required Before Merge To Main)
1. Open `solutions/game/fps-gaze-prototype/Unreal/fps-gaze-prototype/FPSGazePrototype.uproject` in Unreal Engine 4.27.
2. Start PIE session.
3. Run `Gaze.ValidateStage1` in the Unreal console.
4. Confirm artifacts are written under `solutions/game/fps-gaze-prototype/artifacts/stage-1/`.
5. Run `Gaze.Toggle` twice and confirm enabled state flips in console output.

Expected deterministic console keywords:
- `Gaze.Enabled=true` or `Gaze.Enabled=false`
- `Gaze.ValidateStage1=ok`

## Notes
- Stage-1 excludes intent, gameplay adapters, and vertical slice work.
- Artifacts contain a single sample shape contract only; no raw gaze time-series output is permitted.
