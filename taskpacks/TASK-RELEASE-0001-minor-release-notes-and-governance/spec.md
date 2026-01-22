# Spec

## Goal

Publish minor release notes for the deterministic review system, confirm Tier-1 governance language remains factual, and align local skills/workflow documentation with the new review runner.

## Context

The repo now includes a deterministic review runner, strict CI enforcement for objective violations, and opt-in pre-push and orchestrator evidence collection. Documentation must reflect what exists without aspirational language or default behavior changes.

## Requirements

- Determine the next minor version from existing tags and release-note conventions.
- Create or update the release notes for the next minor version with factual changes only.
- Ensure `docs/GOVERNANCE.md` describes the deterministic review system accurately and contract-safely.
- Update skills/workflow documentation to reference the deterministic review runner and report schema.
- Keep changes small and doc-focused; no runtime behavior changes.

## Non-Goals

- No new review checks or enforcement changes.
- No new tooling dependencies.
- No network access.
