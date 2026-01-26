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

## Deterministic Review System

Purpose:
- Provide deterministic, repo-wide checks that enforce objective requirements for Tier 1 documentation, release notes presence, and Task Pack required files.

Scope of checks:
- Presence of Tier 1 documents and release notes artifacts.
- Presence of required Task Pack files (task.yml, spec.md, acceptance.yml, risk.md, runbook.md).
- No content analysis, heuristic inference, or AI/LLM usage.

Enforcement model:
- Local usage is advisory by default via the pre-push hook; strict mode is opt-in for local runs.
- CI runs the same runner in strict mode and blocks only on objective violations (exit code 2).
- Runner errors return exit code 1 and fail CI as execution errors, not as violations.

Source of truth:
- The JSON report produced by `tools/review.run_review` via `--report-path`
  (for example, `review_report.json` in CI and `.orchestrator_logs/<run_id>/review_report.json`
  when collected) is the authoritative record.
- Review report schema version: 1.
- Extension guidance: `docs/review/DETERMINISTIC_REVIEW.md`.

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
