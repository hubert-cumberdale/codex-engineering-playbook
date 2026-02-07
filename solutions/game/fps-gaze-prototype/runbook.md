# Runbook — FPS Gaze Prototype Task Pack

## Purpose
Provide deterministic, command-based steps for a new agent to set up prerequisites, open the Unreal project, verify Tobii signal presence, toggle eye tracking, and reproduce the vertical slice.

## Prerequisites
- Windows 10 or 11 PC.
- Unreal Engine 4.27 installed via Epic Games Launcher or source build.
- Visual Studio 2019 with the C++ workload.
- Tobii Eye Tracking runtime installed and a supported device connected (optional).
- Git client.

## Repository Setup
1. Clone the repository.
2. Confirm the Task Pack exists at `solutions/game/fps-gaze-prototype/`.
3. Ensure the Unreal project root path matches `spec.md`.

## Open the Unreal Project
1. Double-click the `.uproject` file defined in `spec.md`.
2. If prompted to rebuild modules, accept and allow the build to complete.
3. Verify the project opens without errors in the Unreal Editor.

## Build Verification (Stage 0 Evidence)
1. Build the project in `Development Editor` and `Win64`.
2. Capture build output to `artifacts/stage-0/build_output.log`.
3. Record engine version and project identifier artifacts:
   - `artifacts/stage-0/engine_version.txt`
   - `artifacts/stage-0/project_id.txt`
4. Record exact commands or clicks used to reproduce the build in `artifacts/stage-0/repro_steps.txt`.

## Verify Tobii Signal Presence (Stage 1 Evidence)
1. Enable the Tobii provider via the project setting in `spec.md`.
2. Launch the project in PIE (Play In Editor).
3. Confirm signal status through the runtime validation output defined in `spec.md`.
4. Save validation output to `artifacts/stage-1/runtime_validation.log`.
5. Record the signal contract to `artifacts/stage-1/signal_contract.md`.
6. Record provider toggle state, selected provider, and sample schema version to `artifacts/stage-1/provider_status.json`.

## Toggle Eye Tracking On/Off
1. Locate the runtime toggle defined in `spec.md` (config key or console command).
2. Set the toggle to `off` and confirm the null provider is active.
3. Set the toggle to `on` and confirm the Tobii provider is active.
4. Record the validation evidence in `artifacts/stage-1/runtime_validation.log`.

## Reproduce Intent Layer Evidence (Stage 2)
1. Enable the intent debug overlay or log output defined in `spec.md`.
2. Exercise aim, interaction, and UI focus behaviors without applying gameplay effects.
3. Save outputs to:
   - `artifacts/stage-2/intent_resolution.log`
   - `artifacts/stage-2/intent_report.json`

## Reproduce Adapter Evidence (Stage 3)
1. Enable the deterministic adapter capture mode defined in `spec.md`.
2. Capture before/after outputs for:
   - Aim assist
   - Interaction
   - UI visibility
   - Camera bias
3. Save outputs to `artifacts/stage-3/` with filenames listed in `acceptance.yml`.

## Reproduce Vertical Slice (Stage 4)
1. Load the arena map defined in `spec.md`.
2. Verify targets, interactables, and HUD widgets are present.
3. Confirm each gaze mechanic is enabled and gated by the eye tracking toggle.
4. Record the checklist and outputs:
   - `artifacts/stage-4/vertical_slice_checklist.txt`
   - `artifacts/stage-4/validation_output.log`
   - `artifacts/stage-4/toggle_matrix.json`
