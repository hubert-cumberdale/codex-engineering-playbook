# Risk Assessment (Security)

## Scope of change
- Evidence generation only
- No system or environment interaction

## Primary risks
1. **False signal**
   - This task does not validate real security posture.
   - Mitigation: Explicitly document this as a contract test.

2. **Overinterpretation**
   - Results could be mistaken for meaningful coverage.
   - Mitigation: Clear non-goals in spec and artifacts.

## Residual risk
- Minimal by design; this task validates process, not posture.

## Rollback plan
- Revert task pack if acceptance logic changes.
