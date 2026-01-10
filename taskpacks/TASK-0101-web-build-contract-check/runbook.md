# Runbook (Web)

## Purpose
This task validates the web task pack contract itself:
- build/test (or deterministic validation) as truth
- no deployment by default
- evidence-first artifacts
- scoped diffs

## How to run
- Run via orchestrator (local or CI)
- No special setup required

## Expected output
- Artifacts under `artifacts/` documenting the build/test contract

## Acceptance
- Artifacts exist
- Artifacts reference build/test/validation as the success signal
- Artifacts do not include deployment language
- No scope violations

## Review guidance
- Confirm this is contract-only (no app changes)
- Confirm the “no deploy” posture is clear
- Confirm acceptance is fully evidence-driven
