# Versioning Policy

Codex Orchestrator follows **Semantic Versioning** with strict interpretation.

Format:

MAJOR.MINOR.PATCH


---

## MAJOR Versions (v2.0.0, v3.0.0)
A MAJOR version is required if **any** of the following change:

- Safety defaults
- Task Pack isolation guarantees
- Execution phase model
- Evidence requirements
- Control plane / data plane separation

MAJOR versions may:
- Introduce new execution models
- Add new abstractions (e.g., security/solutions/bas_core)
- Change agent autonomy semantics

---

## MINOR Versions (v1.1.0, v1.2.0)
MINOR versions may add **capabilities** without breaking contracts.

Allowed changes:
- New skills
- New Task Pack templates
- Additional validation
- New tooling integrations
- Performance improvements

MINOR versions must not:
- Weaken safety
- Remove required artifacts
- Change existing schemas incompatibly

---

## PATCH Versions (v1.0.1, v1.0.2)
PATCH versions are **fix-only**.

Allowed:
- Bug fixes
- Documentation corrections
- Logging improvements
- CI reliability fixes

Disallowed:
- Behavioral changes
- New features
- Schema changes

---

## Contract Lock Rule
Once a MAJOR version is released:
- Its guarantees are frozen
- Violations require a new MAJOR version
- “Temporary exceptions” are not allowed

---

## Deprecation Policy
- Features are deprecated only in MINOR releases
- Removal occurs only in the next MAJOR release
- Deprecations must be documented with rationale

---

## Version Authority
- Version bumps are intentional, reviewed decisions
- Tagging a release asserts contractual intent

If in doubt:
**Do not bump the version. Fix the design instead.**
