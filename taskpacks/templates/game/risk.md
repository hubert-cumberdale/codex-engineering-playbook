# Risk Assessment (Game)

## Scope of change
- **In scope:** deterministic gameplay logic, state machines, tooling, content pipelines, build/export config, docs
- **Out of scope:** subjective tuning (“feel”), manual playtest-based acceptance, live services/telemetry

## Primary risks
1. **Non-determinism**
   - Risk: Behavior changes depend on timing, frame rate, or environment.
   - Mitigation: Prefer headless validation; fix seeds where relevant; pin engine/tool versions.

2. **Engine/version incompatibility**
   - Risk: Changes work only for one local setup and break in CI or on other machines.
   - Mitigation: Declare engine + version explicitly; avoid relying on editor-only state.

3. **Asset or content pipeline breakage**
   - Risk: Renames/moves break references; exports fail silently.
   - Mitigation: Validate via headless checks/build steps; keep changes scoped; document asset conventions.

4. **“Looks fine” acceptance**
   - Risk: Success criteria become subjective or require manual playtesting.
   - Mitigation: Acceptance must be deterministic and machine-checkable; forbid playtest-only criteria.

## Safety & reproducibility guarantees (v1)
- No implicit network access
- No implicit cloud/environment mutation
- No secrets
- Deterministic validation preferred
- No hidden runtime state outside declared artifacts

## Residual risk
- Some issues (performance, UX, “feel”) cannot be validated in this system by design.
- Platform-specific behavior may require dedicated platform validation taskpacks.

## Rollback / recovery plan
- Revert PR or revert commit(s).
- If the task requires subjective tuning: move tuning to a separate process outside this system.
- If validation is unreliable: tighten acceptance to deterministic signals (logs/build/export).
