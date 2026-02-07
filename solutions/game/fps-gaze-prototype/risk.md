# Risk & Ethics — FPS Gaze Prototype

## Eye Tracking Availability Risk
- Risk: Tobii runtime or device is unavailable on some systems.
- Impact: Gaze features fail or block gameplay.
- Mitigation: Null provider fallback is default; all gameplay remains functional without eye tracking.
- Evidence: Stage 1 runtime validation shows provider switching.

## Plugin / Engine Version Drift
- Risk: Tobii plugin compatibility diverges from Unreal Engine 4.27 baseline.
- Impact: Build failures or runtime crashes.
- Mitigation: Record exact engine and plugin versions in Stage 0 and Stage 1 artifacts; gate upgrades through explicit acceptance updates.
- Evidence: `artifacts/stage-0/engine_version.txt`, `artifacts/stage-1/signal_contract.md`.

## Player Comfort & Camera Motion
- Risk: Gaze-based camera bias causes discomfort or motion sickness.
- Impact: Negative player experience and accessibility concerns.
- Mitigation: Use bounded micro-bias, provide opt-out toggle, and keep mouse as primary control.
- Evidence: Stage 3 adapter capture shows capped camera bias values.

## Accessibility & Opt-Out
- Risk: HUD visibility changes make critical information inaccessible or non-obvious.
- Impact: Reduced accessibility and task completion issues.
- Mitigation: Define gaze zones that never hide critical HUD elements; provide toggle to disable gaze-based HUD behavior.
- Evidence: Stage 3 UI adapter captures and Stage 4 checklist confirm behavior.

## Data Handling & Ethics
- Risk: Gaze data is stored or exported unintentionally.
- Impact: Privacy violation and policy breach.
- Mitigation: Disallow raw gaze logging and enforce intent-only data flows.
- Evidence: Stage 1 signal contract and code review checks in later stages.
