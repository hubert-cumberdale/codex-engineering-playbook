# Governance: Detection Strategy Generator

This governance policy controls changes, versioning, and release discipline.

---

## 1) Versioning
The generator must use semantic versioning:

- **MAJOR**: contract changes (section structure, provenance rules, determinism inputs)
- **MINOR**: new features that do not break contract (new providers, new templates, new indexes)
- **PATCH**: bug fixes that do not change contract outputs for the same inputs

Any change to `DETECTION_STRATEGY_CONTRACT.md` implies at least a MINOR bump;
breaking contract implies a MAJOR bump.

---

## 2) Change control
### Required PR contents for any change
- Updated docs (if contract/governance/source-of-truth changes)
- Tests updated or added
- If outputs change: golden diffs + justification
- Provenance/determinism impacts documented

### Review gates
- Contract review required for:
  - ADS section structure
  - provenance fields
  - determinism rules
  - source-of-truth rules
- Security review required for:
  - new rule providers (auth, secrets handling)
  - network fetch behavior
  - handling of sensitive identifiers in profiles

---

## 3) Release discipline
A release MUST include:
- generator version
- template version/hash
- default pinned ATT&CK STIX version/hash
- changelog entry (what changed, why it’s safe)

A release MUST NOT:
- enable `latest` fetching by default
- remove provenance fields
- weaken determinism requirements

---

## 4) Profile governance
Profiles/overlays are operational truth and must be reviewed like configuration-as-code:
- schema validated
- versioned
- environment-specific secrets must not be stored in repo
- references to secrets must use environment variables or secret managers (implementation stage)

---

## 5) Rule provider governance
Rule provider enablement must be explicit:
- disabled by default unless configured in profile
- pinned dataset versions for offline providers
- provenance recorded in every doc

---

## 6) Compliance and audit requirements (CTEM-friendly)
Generated documents must be auditable:
- provenance included per doc
- deterministic reproduction possible
- explicit handling of telemetry gaps
- no invented claims of coverage or effectiveness
