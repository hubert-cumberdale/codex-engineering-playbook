# Design — TP-03 Intent (Stage-2)

## Engine Target
- Unreal Engine 4.27, Win64 Development Editor.

## Stage-2 Architecture
- Module: `FPSGazeCore`
  - Stage-1 provider subsystem remains the source of normalized and confidence-gated samples.
  - Stage-2 adds a pure intent resolver (`FGazeIntentResolver`) and intent output types.
  - Resolver has no side effects and does not apply gameplay, camera, UI, or map mutations.

No new Unreal module is added because the resolver is lightweight and belongs to the existing `FPSGazeCore` contract boundary.

## Data Flow (No Side Effects)
1. Provider subsystem supplies a normalized sample (`FGazeSampleNormalized`) with Stage-1 gating semantics.
2. Stage-2 resolver receives:
   - a fixture case containing `stage1_provider_snapshot` (verbatim Stage-1 snapshot object),
   - resolver settings (`enabled`, `provider`, `confidence threshold`),
   - fixture-style scene model (targets + UI zones).
3. Resolver emits pure outputs:
   - `AimIntentTarget`
   - `InteractIntentTarget`
   - `UIFocusZone`

The resolver does not call gameplay adapters, does not mutate actors/widgets, and does not execute traces/raycasts.

## Stage-2 Invariants
- Fixtures embed the Stage-1 provider snapshot object verbatim under `stage1_provider_snapshot`; no translation layer is allowed.
- Boundary checks compute and compare a Stage-1 snapshot schema fingerprint against every fixture case.
- Any Stage-1 snapshot schema change requires fixture updates and is enforced as a hard failure by `check_stage2_boundaries.py`.
- Fixtures use `resolver_config.confidence_min_q` (integer) as the confidence gate source; per-case thresholds are not allowed.
- Fixtures declare `fixtures_sha256` and it is computed from normalized JSON: load fixture JSON, set `fixtures_sha256` to `""`, serialize with sorted keys and compact separators, then sha256 that payload.
- Boundary and artifact checks enforce that declared `fixtures_sha256` matches the normalized computation and that `intent_report.json.inputs.fixtures_sha256` matches the fixtures file value.
- Fixture expectations use `expect` with required keys: `aim_intent_target_id`, `interact_intent_target_id`, `ui_focus_zone_id`, `reason_code`, `tie_break`.
- UI precedence is hard-locked: if `ui_focus_zone_id` is non-null, both `aim_intent_target_id` and `interact_intent_target_id` must be null.
- Stage-2 remains intent-only: no adapters, no gameplay effects, no time-series logging, and no smoothing/dwell/history logic.

## Deterministic Scene Model
Fixtures define a synthetic scene independent of engine runtime:
- Targets:
  - `id`
  - `types` (`aimable`, `interactable`, `ui`)
  - `screen_region` (`min_x`, `min_y`, `max_x`, `max_y`)
  - `priority` (integer)
  - `tags` (string array)
- UI zones:
  - `name`
  - `screen_region`

All coordinates are normalized viewport space `[0.0, 1.0]` with origin top-left.

## Resolver Rules
1. Input suppression:
   - If `enabled=false` OR `provider=Null` OR `present=false` OR `confidence < threshold`, then:
     - `AimIntentTarget = null`
     - `InteractIntentTarget = null`
     - `UIFocusZone = null`
2. Candidate generation:
   - A target is a candidate when gaze point is inside `screen_region`.
3. Target resolution:
   - `AimIntentTarget`: choose candidates tagged `aimable`.
   - `InteractIntentTarget`: choose candidates tagged `interactable` or `ui`.
   - Tie-break: highest `priority`, then lexical ascending `id`.
4. UI zone resolution:
   - First matching zone by priority/id ordering rule applied to zones via declared list order.
   - If no zone hit, `UIFocusZone = null`.

## Determinism Guarantees
- Resolver order is explicit and stable.
- Tie-break order is explicit and stable.
- Artifacts are generated with sorted JSON keys and deterministic snapshot iteration.
- No time-based randomization, world state reads, raycasts, or async dependency.

## Fixture Coverage
Fixtures include cases for:
- low confidence gating
- provider null
- overlapping regions with tie-break
- no hit -> null intent
- disabled and not-present gating
