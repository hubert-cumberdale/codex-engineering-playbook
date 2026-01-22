# Repo Review

## Purpose
- Produce an advisory, repo-wide review of the requested scope.

## Scope
- Review repository content only; make no changes.
- Limit output to findings and a next prompt.

## Hard Constraints
- Do not change files.
- Do not propose or implement fixes.
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
- Findings list with concrete file references.
- next_prompt content aligned to .codex/next_prompt.yml.

## Acceptance Criteria
- Output is advisory only.
- Output includes findings and a next_prompt.
- No files are modified.

## Explicit Non-Goals
- No fixes, patches, or refactors.
- No policy reinterpretation.

## Stop Conditions
- Stop if the request requires solution-specific logic.
- Stop if the request requires orchestrator changes.
