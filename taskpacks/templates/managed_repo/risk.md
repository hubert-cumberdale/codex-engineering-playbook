# Risk Assessment (Managed Repo)

## Scope of change
- **In scope:** code and config changes within declared paths; docs updates required by the task
- **Out of scope:** production deployments, infrastructure mutations, unmanaged repositories

## Primary risks
1. **Regression / breaking changes**
   - Risk: Changes break existing behavior or compatibility.
   - Mitigation: Require tests and validation; keep diffs small and reviewable.

2. **Governance drift**
   - Risk: Changes violate target repo rules or current work constraints.
   - Mitigation: Read and follow `docs/GOVERNANCE.md` and `docs/CURRENT_WORK.md`.

3. **Accidental scope expansion**
   - Risk: Changes touch files outside allowed paths or task intent.
   - Mitigation: Use `scope.allowed_paths` and keep acceptance scoped.

4. **Dependency or tooling instability**
   - Risk: New dependencies introduce instability or slowdowns.
   - Mitigation: Minimize new deps; document rationale; pin versions when possible.

## Safety & reproducibility guarantees (v1)
- No implicit network access
- No implicit cloud/environment mutation
- No secrets
- Acceptance prefers machine-checkable tests
- No implicit state outside the repo

## Residual risk
- Some regressions may only surface under production usage or specific environments.
- Dependency changes can have delayed downstream effects.

## Rollback / recovery plan
- Revert PR or revert commit(s) if regressions are found.
- If scope becomes too large: split into follow-on task packs with clear acceptance.
