# Contract — TP-02 Provider (Stage-1)

## Scope Anchor
This Task Pack implements only Stage-1 from `solutions/game/fps-gaze-prototype/spec.md` and `solutions/game/fps-gaze-prototype/acceptance.yml`.

Global constraints and invariants are inherited from:
- `solutions/game/fps-gaze-prototype/contract.md`
- `solutions/game/fps-gaze-prototype/spec.md`
- `solutions/game/fps-gaze-prototype/acceptance.yml`

## Stage-1 Local Invariants
- C++ provider interface is Blueprint-accessible.
- Runtime selection supports `Tobii` and `Null`.
- Runtime enable state is controlled by `Gaze.Enabled` and `Gaze.Toggle`.
- Provider selection is controlled by `Gaze.Provider` (`Tobii|Null`).
- Normalized sample schema includes: `gaze_x`, `gaze_y`, `confidence`, `present`, `source`, `timestamp`.
- Confidence gating executes before downstream usage.
- Null provider is default-safe and returns no gaze.
- Tobii SDK touchpoints are confined to Tobii provider implementation.
- Deterministic Stage-1 artifacts are produced under `solutions/game/fps-gaze-prototype/artifacts/stage-1/`.

## Explicit Exclusions
- No Stage-2 intent resolution.
- No Stage-3 gameplay adapters.
- No Stage-4 map/HUD/slice work.
- No raw gaze time-series logging, recording, export, or telemetry pipelines.
