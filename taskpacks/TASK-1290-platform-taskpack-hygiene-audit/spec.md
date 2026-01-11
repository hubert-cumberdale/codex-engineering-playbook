# TASK-1290 — Platform hygiene audit

## Goal
Provide a repeatable, evidence-first hygiene audit that scans:
- Task Pack structure
- Acceptance command patterns
- Common Python import footguns
- Determinism red flags in artifacts/docs

## In scope
- Static scanning only
- Heuristic checks (non-blocking)
- Deterministic report artifacts

## Out of scope
- No enforcement
- No orchestrator or validator changes
- No CI gating

## Reviewer checklist
- [ ] `hygiene_report.json` exists and is machine-readable
- [ ] `hygiene_report.md` summarizes findings clearly
- [ ] No network or environment assumptions
