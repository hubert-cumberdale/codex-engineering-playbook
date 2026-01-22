# CI Workflow

## Purpose
- Define repo-wide GitHub Actions workflow changes.

## Scope
- Apply to GitHub Actions only.
- Prefer additive changes by default.

## Hard Constraints
- Do not change orchestrator semantics.
- Do not add solution-specific logic.
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
- GitHub Actions workflow updates.
- Validation commands, if applicable.

## Acceptance Criteria
- Changes are additive by default.
- No non-GitHub Actions CI systems are modified.

## Explicit Non-Goals
- No runtime or orchestrator changes.
- No solution-specific pipelines.

## Stop Conditions
- Stop if the request targets non-GitHub Actions CI.
- Stop if the request requires solution-specific logic.
