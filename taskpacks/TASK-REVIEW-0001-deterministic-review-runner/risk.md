# Risk Assessment

## Scope of change
- **In scope:** new deterministic review runner and unit tests
- **Out of scope:** orchestrator runtime behavior, networked checks, heuristic analysis

## Primary risks
1. **False negatives**
   - Risk: Required files exist but are missed due to path or glob errors.
   - Mitigation: Use fixed path lists and deterministic iteration.

2. **False positives**
   - Risk: Report flags violations due to unstable ordering or inconsistent rules.
   - Mitigation: Fixed check registry, sorted iteration, stable JSON serialization.

3. **Process disruption**
   - Risk: New tooling could interfere with existing workflows.
   - Mitigation: Keep tool additive and standalone; no runtime behavior changes.

## Safety & reproducibility guarantees
- No network access
- Deterministic filesystem inspection only
- Stable JSON report output

## Rollback plan
- Revert the review runner files and associated tests.
