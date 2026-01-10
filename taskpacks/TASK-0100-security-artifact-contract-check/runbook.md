# Runbook (Security)

## Purpose
This task validates the security task pack contract itself.

## How to run
- Run via orchestrator (local or CI)
- No special setup required

## Expected output
- A simple artifact under `artifacts/` documenting a mock finding

## Acceptance
- Artifacts exist
- Artifacts contain explicit results
- No scope violations

## Review guidance
- Confirm acceptance is driven purely by evidence
- Confirm no implicit behavior or unsafe actions occurred
