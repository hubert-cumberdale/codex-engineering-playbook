# Codex Orchestrator v1.2.0 — Pressure Reduction & Hygiene

> Status: Planned  
> Scope: Documentation, templates, hygiene Task Packs  
> No orchestrator or validator behavior changes

---

## Summary

v1.2.0 focuses on **reducing contributor friction** and **improving review ergonomics**
without altering the Codex Orchestrator execution model.

This release operationalizes lessons learned from v1.x usage into:
- clearer templates
- explicit patterns
- routine hygiene audits

---

## What’s new

### 🧹 Platform Hygiene

- New hygiene Task Pack:
  - `TASK-1290-platform-taskpack-hygiene-audit`
- Provides deterministic, evidence-first reports on:
  - Task Pack structure
  - Acceptance command patterns
  - Import path footguns
  - Determinism smells
  - Documentation language hygiene

Findings are **informational only**.

---

### 📋 v1.2 Pressure Checklist

- Added Tier-2 pressure checklist documenting:
  - Known v1.x friction points
  - Recommended patterns
  - “Done means” criteria
- Serves as planning and review guidance, not enforcement.

---

### 📐 Template & Guidance Improvements (Planned)

- Explicit Python import path patterns
- Standardized unittest discovery commands
- Deterministic artifact rules
- Optional multi-artifact manifest pattern
- Improved runbook snapshot guidance

---

## What did *not* change

- ❌ No orchestrator logic
- ❌ No new validators
- ❌ No new flags or execution paths
- ❌ No enforcement added to CI

---

## Upgrade notes

- Existing Task Packs remain valid and unchanged.
- New Task Packs are encouraged (but not required) to follow v1.2 guidance.

---

## Next steps

- Update templates and walkthroughs to reflect v1.2 patterns
- (Optional) Add a non-gating CI workflow to run hygiene audits
- Collect feedback from real Task Pack usage

---

## Compatibility

- Fully compatible with v1.1.x
- No migration required