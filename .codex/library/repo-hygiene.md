# Repo Hygiene

## Purpose
- Enforce repo cleanliness without changing meaning or behavior.

## Scope
- Apply repo-wide hygiene only.
- Limit changes to formatting, structure, or organization.

## Hard Constraints
- Do not change semantics or behavior.
- Do not add solution-specific logic.
- Do not change orchestrator semantics.
- Do not add AI behavior.

## Authoritative Sources
- AGENTS.md
- docs/GOVERNANCE.md
- docs/Canonical Conventions.md
- docs/DOC_CHECKLIST_TIER1.md
- docs/Current Status.md
- docs/System Overview.md
- docs/Architecture & Roadmap.md

## Deliverables
- Minimal, deterministic hygiene changes.
- Validation commands, if applicable.

## Acceptance Criteria
- Changes are repo-wide and purely hygienic.
- No semantic drift is introduced.

## Explicit Non-Goals
- No feature or behavior changes.
- No content rewrites.

## Stop Conditions
- Stop if a change would alter meaning or behavior.
- Stop if the request requires solution-specific logic.
