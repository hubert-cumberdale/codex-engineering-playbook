# Risk Assessment (Managed Repo Smoke)

## Scope of change
- **In scope:** managed workspace execution and acceptance in aiq-cli
- **Out of scope:** production deployments, cloud mutations, code changes

## Primary risks
1. **Workspace misrouting**
   - Risk: commands run in the playbook repo instead of the managed repo.
   - Mitigation: workspace resolution via registry and cwd enforcement.

2. **Evidence leakage into playbook repo**
   - Risk: evidence written under this repo when running in managed mode.
   - Mitigation: evidence routing enforces workspace/evidence_dir targets.

3. **Scope drift**
   - Risk: changes occur outside `docs/`.
   - Mitigation: `scope.allowed_paths` enforcement.

## Residual risk
- External repo state may differ from expected baseline.

## Rollback / recovery plan
- Revert the taskpack if routing or scope checks fail.
