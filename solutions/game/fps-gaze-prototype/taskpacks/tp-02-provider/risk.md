# Risk Register — TP-02 Provider (Stage-1)

## Risk: Tobii runtime/device unavailable
- Impact: Tobii provider cannot produce live gaze.
- Mitigation: Default to Null provider, keep gameplay path operational without hardware.
- Evidence: `artifacts/stage-1/provider_status.json` and `artifacts/stage-1/runtime_validation.log` show fallback state.

## Risk: Unreal/Tobii plugin API drift
- Impact: Provider integration compile/runtime incompatibility.
- Mitigation: Constrain Tobii calls to one provider implementation and isolate via compile guards.
- Evidence: Stage-1 source boundary check and documented integration surface in `design.md`.

## Risk: Confidence gating threshold drift
- Impact: Inconsistent suppression semantics across environments.
- Mitigation: Declare a fixed threshold and deterministic fixture-based validation.
- Evidence: `artifacts/stage-1/runtime_validation.log` includes threshold and gating summary.

## Risk: Stage boundary leakage
- Impact: Intent or gameplay work appears in Stage-1 scope.
- Mitigation: Automated boundary lint for disallowed Stage-2/3/4 terms in Stage-1 code paths.
- Evidence: `tools/check_stage1_boundaries.py` in acceptance commands.
