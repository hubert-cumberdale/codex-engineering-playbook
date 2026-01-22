# Risk Assessment

## Summary
Low risk. Changes are additive and opt-in, with deterministic behavior enforced by tests.

## Risks and Mitigations
- Risk: schema changes break consumers.
  - Mitigation: versioned schema header and stable ordering; tests cover header and violations.
- Risk: orchestrator behavior changes by default.
  - Mitigation: collection only when `ORCH_COLLECT_REVIEW=1` is set; non-fatal status recorded.
