# Risk Assessment

## Scope of change
- **In scope:** CI workflow integration for the deterministic review runner and governance documentation updates
- **Out of scope:** orchestrator runtime behavior, new review checks, networked or heuristic analysis

## Primary risks
1. **Unexpected CI blocking**
   - Risk: CI blocks for non-objective reasons.
   - Mitigation: Run the existing deterministic runner in strict mode and block only on exit code 2.

2. **Missing audit artifact**
   - Risk: Review report is not available after a failure.
   - Mitigation: Upload `review_report.json` with `if: always()`.

3. **Governance drift**
   - Risk: Tier 1 docs do not reflect actual enforcement.
   - Mitigation: Update `docs/GOVERNANCE.md` with explicit, factual review system semantics.

## Safety & reproducibility guarantees
- No network access during review execution
- Deterministic, file-based checks only
- CI enforces only objective violations

## Rollback plan
- Revert the CI workflow and governance changes for the review system.
