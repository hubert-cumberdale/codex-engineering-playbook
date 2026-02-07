# Artifacts

This Task Pack writes evidence under `artifacts/TASK-3000/`.

Expected evidence:
- `contract.txt` describing the deterministic headless validation intent.
- `build_metadata.json` capturing engine name/version and WebAssembly target.
- `build_log.txt` showing deterministic export steps.
- `deterministic_validation.log` showing the scripted headless run.
- `asset_manifest_summary.txt` listing NASA imagery sources and local paths.

Artifacts must be deterministic and reviewable without running the Task Pack.
