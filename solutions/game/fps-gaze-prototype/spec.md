# Specification — FPS Gaze Prototype Task Pack

## Repository Layout (Required)
- Unreal project root: `Game/fps-gaze-prototype/` or `Unreal/fps-gaze-prototype/`
- Unreal project file: `Game/fps-gaze-prototype/FPSGazePrototype.uproject` or `Unreal/fps-gaze-prototype/FPSGazePrototype.uproject`
- Source modules:
  - `FPSGazePrototype` (gameplay, adapters, maps)
  - `FPSGazeCore` (provider, signal processing, intent layer)
- Content:
  - `fps-gaze-prototype/Content/Maps/Arena.umap`
  - `fps-gaze-prototype/Content/UI/` (HUD widgets)

## Engine Baseline
- Engine: Unreal Engine 4.27 (Windows PC target).
- Build configuration: `Development Editor`, `Win64`.

## Input & Provider Abstraction
- Mouse/Keyboard remain primary input.
- Eye tracking is optional and gated by provider selection.
- Provider interface exists in C++ and is accessible in Blueprints.
- Required provider types:
  - `Tobii` provider (SDK integration behind interface).
  - `Null` provider (always available, returns no gaze).

## Signal Processing Contract
- Signals are normalized to a declared coordinate space:
  - Screen-space: normalized viewport coordinates (0.0–1.0, origin top-left), or
  - World-space: normalized direction vectors in engine coordinates.
- The chosen coordinate space MUST be declared in `spec.md` and remain consistent.
- When confidence gating suppresses intent, intent outputs MUST resolve to explicit null / empty states.
- No raw gaze logging: signals are transient in memory and may only be surfaced via
  normalized status or intent-level artifacts.


## Intent Layer Contract
- Intent outputs include:
  - `AimIntentTarget` (actor or location).
  - `InteractIntentTarget` (actor or UI element).
  - `UIFocusZone` (named HUD region).
- Intent layer has no gameplay side effects.
- Given identical scene state and synthetic gaze inputs, intent outputs MUST be deterministic.

## Gameplay Adapters
- Aim Assist Adapter: blends mouse aim with `AimIntentTarget` using bounded influence.
- Interaction Adapter: highlights and confirms interaction on `InteractIntentTarget`.
- UI Adapter: toggles HUD visibility based on `UIFocusZone`.
- Camera Adapter: applies micro camera bias based on gaze intent.

## Runtime Toggles
- Config key: `Gaze.Enabled` in `Config/DefaultGame.ini`.
- Provider selector key: `Gaze.Provider` with values `Tobii` or `Null`.
- Console command: `Gaze.Toggle` to switch `Gaze.Enabled` at runtime.
- Runtime toggle state MUST be reflected in provider_status.json during validation.

## Deterministic Evidence Artifacts
All artifacts live under `solutions/game/fps-gaze-prototype/artifacts/`.

- Artifacts MUST be text-based or structured (txt, json, md).
- Artifacts MUST be reproducible given identical inputs and environment.
- Artifacts MUST NOT contain raw gaze time-series data.


### Stage 0
- `artifacts/stage-0/engine_version.txt` contains engine version string.
- `artifacts/stage-0/project_id.txt` contains project name and `.uproject` path.
- `artifacts/stage-0/build_output.log` contains build output captured from the editor or build tool.
- `artifacts/stage-0/repro_steps.txt` lists exact commands or clicks used for build verification.

### Stage 1
- `artifacts/stage-1/signal_contract.md` defines signal fields and ranges.
- `artifacts/stage-1/runtime_validation.log` records provider status and gating results.
- `artifacts/stage-1/provider_status.json` records provider toggle state, selected provider, and sample schema version.

### Stage 2
- `artifacts/stage-2/intent_resolution.log` records intent outputs for test scenarios.
- `artifacts/stage-2/intent_report.json` captures fixed scene targets mapped to expected intent outputs.

### Stage 3
- `artifacts/stage-3/aim_assist_metrics.json` captures aim blending deltas.
- `artifacts/stage-3/interaction_metrics.json` captures highlight/confirm state transitions.
- `artifacts/stage-3/ui_state_transitions.json` captures HUD visibility state transitions.
- `artifacts/stage-3/camera_offset_metrics.json` captures camera bias deltas.

### Stage 4
- `artifacts/stage-4/vertical_slice_checklist.txt` lists required elements and pass/fail status.
- `artifacts/stage-4/validation_output.log` records runtime verification output.
- `artifacts/stage-4/toggle_matrix.json` records toggle on/off and provider selection expectations.

## Stage Boundaries (Required)
- Stage 0 ends after a build succeeds and evidence is captured.
- Stage 1 ends after provider abstraction and validation outputs exist.
- Stage 2 ends after intent outputs exist without gameplay effects.
- Stage 3 ends after adapters are wired to intent outputs.
- Stage 4 ends after arena map and four mechanics are active with evidence.
- Advancing a stage while violating a prior stage’s prohibitions constitutes failure.


## Deterministic Validation
- Evidence artifacts are the source of truth for acceptance.
- Validation must be repeatable by a new agent using only the runbook and artifacts.
- Any change to stage boundaries requires updating `acceptance.yml` and this spec.

