# Spec

## Goal

## Context

## Requirements

## Hygiene (v1.2, advisory)

This section provides **non-blocking hygiene guidance** for authoring and reviewing this task pack.
It does **not** change acceptance criteria or execution behavior.

Recommended defaults:
- Acceptance remains **command-based and local**, as defined in `acceptance.yml`.
- Evidence artifacts should be written to stable paths under `artifacts/<taskpack-id>/` with
  deterministic filenames (avoid timestamps in filenames).
- If multiple artifacts are produced, consider adding
  `artifacts/<taskpack-id>/manifest.json` to enumerate outputs and identify primary evidence.
- If report-like output is generated, consider committing an expected snapshot under `expected/`
  and documenting regeneration steps in the runbook.

This guidance is **Tier-2 (informational)** and advisory only.

## Non-Goals
