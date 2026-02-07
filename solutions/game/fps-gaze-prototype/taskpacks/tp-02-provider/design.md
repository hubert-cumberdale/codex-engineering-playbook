# Design — TP-02 Provider (Stage-1)

## Engine Target
- Unreal Engine 4.27, Win64 Development Editor.

## Stage-1 Architecture
- Module: `FPSGazeCore`
  - Defines normalized signal schema and provider interface.
  - Hosts provider runtime selection and enable toggle logic.
  - Implements console commands `Gaze.Toggle` and `Gaze.ValidateStage1`.
- Providers:
  - `UNullGazeProvider`: default-safe no-gaze provider.
  - `UTobiiGazeProvider`: Tobii integration surface behind interface with compile/runtime availability checks.

No Stage-2 intent layer and no Stage-3/4 adapter logic are included.

## Interfaces and Types
- `FGazeSampleNormalized` (`USTRUCT(BlueprintType)`)
  - `gaze_x` (`float`, normalized 0..1)
  - `gaze_y` (`float`, normalized 0..1)
  - `confidence` (`float`, normalized 0..1)
  - `present` (`bool`)
  - `source` (`EGazeProviderSource`, `Tobii|Null`)
  - `timestamp` (`double`, monotonic seconds)
- `IGazeProviderInterface` (`UINTERFACE(BlueprintType)`)
  - `GetLatestSample()`
  - `IsAvailable()`
  - `GetProviderSource()`

## Configuration and Runtime Controls
- `Config/DefaultGame.ini`
  - `Gaze.Enabled=true|false`
  - `Gaze.Provider=Tobii|Null`
  - `Gaze.ConfidenceThreshold=0.60`
- Runtime command:
  - `Gaze.Toggle`
- Validation command:
  - `Gaze.ValidateStage1`

## Confidence Gating
- Threshold is fixed at `0.60` for Stage-1.
- Gating is applied in subsystem before any downstream usage.
- If gated, output sample is explicit no-gaze (`present=false`, `confidence=0.0`, `gaze_x=0.0`, `gaze_y=0.0`) while preserving source and timestamp.

## Module Boundary Rules
- Tobii SDK symbols are permitted only in `.../Private/Providers/TobiiGazeProvider.cpp`.
- No `FPSGazePrototype` gameplay module usage of Tobii SDK symbols.
- Stage-1 acceptance script checks this boundary.

## Deterministic Validation Pathway
- Validation can run without Tobii hardware.
- Deterministic pathway:
  - `python solutions/game/fps-gaze-prototype/taskpacks/tp-02-provider/tools/generate_stage1_artifacts.py`
- Unreal runtime pathway (when engine is available):
  - Use `Gaze.ValidateStage1` console command to emit equivalent Stage-1 artifacts.

## Evidence Formats
- `artifacts/stage-1/signal_contract.md`
  - Field definitions, ranges, and semantics.
- `artifacts/stage-1/runtime_validation.log`
  - Enabled state, selected provider, threshold, provider availability, and deterministic gating summary counts.
- `artifacts/stage-1/provider_status.json`
  - `schema_version`, `enabled`, `provider`, `source`, `threshold`, and one sample shape object.

No raw gaze stream or time-series arrays are emitted.
