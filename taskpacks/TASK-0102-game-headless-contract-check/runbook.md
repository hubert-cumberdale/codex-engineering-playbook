# Runbook (Game)

## Purpose
This task validates the game task pack contract itself:
- deterministic/non-interactive validation as truth
- explicit engine/version intent
- no subjective or playtest-based acceptance
- evidence-first artifacts
- scoped diffs

## How to run
- Run via orchestrator (local or CI)
- No special setup required

## Expected output
- Artifacts under `artifacts/` documenting the validation contract

## Acceptance
- Artifacts exist
- Deterministic/headless validation is explicitly referenced
- Engine/version intent is explicitly declared
- No playtest/subjective criteria appear
- No scope violations

## Review guidance
- Confirm this is contract-only (no game code changes)
- Confirm determinism + engine/version are explicit
- Confirm acceptance is objective and evidence-driven
