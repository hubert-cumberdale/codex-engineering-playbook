# Contract — TP-03 Intent (Stage-2)

## Scope Anchor
This Task Pack implements only Stage-2 from `solutions/game/fps-gaze-prototype/spec.md` and `solutions/game/fps-gaze-prototype/acceptance.yml`.

Global constraints and invariants are inherited from:
- `solutions/game/fps-gaze-prototype/contract.md`
- `solutions/game/fps-gaze-prototype/spec.md`
- `solutions/game/fps-gaze-prototype/acceptance.yml`

## Stage-2 Local Invariants
- Intent outputs are defined as:
  - `AimIntentTarget` (actor id or explicit location).
  - `InteractIntentTarget` (actor id or UI element id reference).
  - `UIFocusZone` (named HUD zone or null).
- Intent resolver consumes normalized/gated sample semantics and settings only.
- If input is suppressed (`enabled=false`, `present=false`, `provider=Null`, or `confidence < threshold`), all intent outputs are explicit null.
- Resolver behavior is deterministic for identical scene model and snapshot fixtures.
- Tie-break rule is deterministic: higher priority first, then stable lexical id order.
- Deterministic Stage-2 artifacts are produced under `solutions/game/fps-gaze-prototype/artifacts/stage-2/`.

## Explicit Exclusions
- No gameplay effects (no aim, camera, interaction trigger, or HUD behavior changes).
- No Stage-3 adapter classes or mechanics (`AimAssist`, `ExtendedView`, `CleanUI`, interaction highlight).
- No raw gaze logging or time-series persistence.
- No content or map changes.
