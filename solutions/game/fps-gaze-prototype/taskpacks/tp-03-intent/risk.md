# Risk Register — TP-03 Intent (Stage-2)

## Risk: Scene dependency drift between fixtures and runtime scenes
- Impact: Runtime perception can differ from deterministic fixture outcomes.
- Mitigation: Keep Stage-2 resolver scene model explicit and fixture-driven; defer runtime raycasts to later stages.
- Evidence: `artifacts/stage-2/intent_report.json` with fixture ids and expected mapping.

## Risk: Non-deterministic tie-break behavior
- Impact: Different output targets for overlapping candidates.
- Mitigation: Enforce strict tie-break (priority desc, id asc) in both design contract and generator.
- Evidence: overlap fixture cases and deterministic report entries.

## Risk: Stage-3/4 creep during Stage-2
- Impact: Adapters or gameplay behavior introduced too early.
- Mitigation: automated boundary script for banned mechanics/tokens and Content/Maps diff checks.
- Evidence: `tools/check_stage2_boundaries.py` output in validation run.

## Risk: Implicit raw gaze logging
- Impact: contract violation and noisy non-deterministic diagnostics.
- Mitigation: artifact checker disallows coordinate stream markers and sample history arrays.
- Evidence: `tools/check_stage2_artifacts.py` checks on Stage-2 artifacts.
