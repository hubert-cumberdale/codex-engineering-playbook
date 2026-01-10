# Risk Assessment (Security)

## Scope of change
- **In scope:** security analysis, validation, evidence generation, documentation updates
- **Out of scope:** production changes, live incident response, privileged access operations, secret handling

## Primary risks
1. **False confidence**
   - Risk: The task produces “pass” results that do not reflect real-world coverage.
   - Mitigation: Ensure artifacts include explicit assumptions, coverage boundaries, and what was not tested.

2. **Overreach / unintended modifications**
   - Risk: Changes spill outside declared scope (e.g., modifying unrelated files or systems).
   - Mitigation: Constrain diffs to approved paths; require review; keep taskpack bounded.

3. **Unsafe execution (network / mutation)**
   - Risk: Task attempts network access or cloud mutations without explicit constraints.
   - Mitigation: Default constraints deny network and cloud mutation; require explicit opt-in and review if needed.

4. **Sensitive data exposure**
   - Risk: Logs, artifacts, or diffs include secrets or sensitive identifiers.
   - Mitigation: Prohibit secret reads; redact outputs; treat artifacts as publishable by default.

## Safety & reproducibility guarantees (v1)
- No implicit network access
- No implicit cloud/environment mutation
- No secrets
- Evidence-first artifacts required
- No long-lived agents or hidden state

## Residual risk (what remains even if we do everything right)
- Results may be incomplete due to limited telemetry, scope constraints, or lack of live verification.
- Findings may require follow-up validation in a controlled environment.

## Rollback / recovery plan
- If code changes were made: revert PR or revert commit(s).
- If artifacts are incorrect: remove/replace artifacts and rerun with clarified assumptions.
- If scope was exceeded: split into smaller taskpacks with tighter acceptance.
