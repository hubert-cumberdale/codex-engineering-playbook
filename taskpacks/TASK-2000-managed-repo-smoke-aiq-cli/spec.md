# Spec

## Goal
Validate that managed workspace execution targets the aiq-cli repo root and runs
acceptance commands locally without writing evidence into this playbook repo.

## Context
This is a minimal smoke taskpack for managed repositories.

## Requirements
- Workspace is resolved via registry name: `aiq-cli`.
- Acceptance runs `pytest` in the workspace root.
- Scope is limited to `docs/` in the managed repo.
- Required docs exist: `docs/UX_MODEL.md`, `docs/GOVERNANCE.md`.

## Non-Goals
- No product behavior changes.
- No network access or cloud mutations.
- No evidence schema changes.
