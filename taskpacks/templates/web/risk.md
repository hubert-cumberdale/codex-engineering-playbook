# Risk Assessment (Web)

## Scope of change
- **In scope:** application code changes, refactors, tests, build configuration, docs
- **Out of scope:** production deployments, infrastructure mutations, live data migrations

## Primary risks
1. **Regression / breaking changes**
   - Risk: Changes break existing behavior or compatibility.
   - Mitigation: Require build/test passing; add/adjust tests; keep diffs small and reviewable.

2. **Contract drift**
   - Risk: API schemas/interfaces change without explicit intent, breaking consumers.
   - Mitigation: Document contract changes in `spec.md`; enforce schema/contract tests if applicable.

3. **Accidental deployment or environment coupling**
   - Risk: Task introduces deploy steps, production assumptions, or environment-specific logic.
   - Mitigation: Default constraints deny cloud mutation; acceptance forbids deployment patterns unless explicitly declared.

4. **Supply chain / dependency risk**
   - Risk: New dependencies introduce vulnerabilities or instability.
   - Mitigation: Minimize new deps; pin versions when possible; document rationale.

## Safety & reproducibility guarantees (v1)
- No implicit network access
- No implicit cloud/environment mutation
- No secrets
- Acceptance prefers machine-checkable tests/builds
- No implicit state outside the repo

## Residual risk
- Some regressions may only surface under production traffic patterns or specific environments.
- Dependency changes can have delayed downstream effects.

## Rollback / recovery plan
- Revert PR or revert commit(s) if regressions are found.
- If scope becomes too large: split into follow-on taskpacks with clear acceptance.
- If dependency changes cause instability: revert dependency bump and isolate to a dedicated taskpack.
