# Risk Assessment

## Scope of change
- **In scope:** advisory pre-push hook tooling and installer scripts
- **Out of scope:** orchestrator runtime behavior, networked checks, enforced gating

## Primary risks
1. **Unintended blocking**
   - Risk: Hook blocks pushes unexpectedly.
   - Mitigation: Advisory by default; strict mode requires explicit env flag.

2. **Hook clobbering**
   - Risk: Existing hooks are overwritten.
   - Mitigation: Backup existing hook before install and restore on uninstall.

3. **Non-deterministic behavior**
   - Risk: Hook behavior differs per environment.
   - Mitigation: Deterministic runner, fixed command, no network access.

## Safety & reproducibility guarantees
- No network access
- Deterministic filesystem inspection only
- Hook is opt-in and advisory by default

## Rollback plan
- Run `python -m tools.review.uninstall_hook` or restore the backed-up hook.
