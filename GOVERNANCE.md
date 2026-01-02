# Governance Model

This document defines how decisions are made in the Codex Engineering Playbook.

The goal is to ensure:
- Intentional evolution
- Contract stability
- Explicit authority
- Controlled autonomy

---

## Decision Domains

### 1. System Contract
Includes:
- Control/Data plane separation
- Safety model
- Task Pack semantics
- Evidence guarantees
- Versioning rules

Authority:
- **MAJOR version only**
- Requires explicit intent

Location of truth:
- EXEC_SUMMARY.md
- VERSIONING.md

---

### 2. Architecture & Design
Includes:
- New abstractions (e.g. security/solutions/bas_core)
- Execution model changes
- Orchestrator behavior

Authority:
- MINOR or MAJOR version
- Design must precede implementation

Location of truth:
- Design docs
- Roadmaps

---

### 3. Capabilities
Includes:
- New skills
- New Task Pack templates
- New adapters

Authority:
- MINOR version
- Must not weaken contracts

Location of truth:
- Skills
- Task Packs

---

### 4. Implementation
Includes:
- Bug fixes
- Refactors
- Performance improvements

Authority:
- PATCH version
- No behavior change

---

## Change Process

1. Identify domain (contract, architecture, capability, implementation)
2. Confirm allowed version scope
3. Update documentation first (if required)
4. Implement
5. Release with correct version bump

If a change does not fit this flow, it is rejected.

---

## Safety Veto

Any contributor may veto a change if it:
- Weakens safety defaults
- Reduces auditability
- Introduces implicit state
- Expands autonomy without bounds

Vetoes must be addressed explicitly.

---

## Anti-Drift Rule

> If behavior changes but documentation does not, the change is invalid.

Documentation is not optional — it is part of the system.

---

## Final Authority

This project values:
- Explicitness over convenience
- Constraints over cleverness
- Stability over velocity

Governance exists to protect those values.
