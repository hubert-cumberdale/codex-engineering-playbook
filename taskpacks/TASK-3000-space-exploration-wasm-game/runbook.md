# Runbook (Game)

This runbook describes how to execute and validate the Task Pack.

## Preconditions

- Godot 4.2.2-stable with Web export templates installed.
- Local toolchain for headless test execution.
- Offline NASA imagery set available in the repo and listed in the asset manifest.

## Run

1. Build the WebAssembly target:
   - `bash taskpacks/TASK-3000-space-exploration-wasm-game/scripts/build_wasm.sh`
2. Run headless validation:
   - `bash taskpacks/TASK-3000-space-exploration-wasm-game/scripts/run_headless_sim.sh`

## Validate

- Confirm `artifacts/TASK-3000/` contains:
  - a deterministic validation log
  - a build metadata file with engine/version and target
  - an asset manifest summary

## Rollback

- Revert the Task Pack change set.
- Restore the previous engine/export template version if builds diverge.
