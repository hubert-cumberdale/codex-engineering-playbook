# Spec

## Goal

Add an opt-in advisory pre-push hook that runs the deterministic review runner.

## Context

Local checks should remain advisory by default and never block pushes unless
explicitly configured via environment variable.

## Requirements

- Provide hook template at `tools/review/hooks/pre-push`.
- Provide installer at `tools/review/install_hook.py`.
- Provide uninstaller at `tools/review/uninstall_hook.py` (optional but recommended).
- Hook runs `python -m tools.review.run_review --mode advisory`.
- Hook does not block pushes unless `CODEX_REVIEW_STRICT=1` is set and
  objective violations exist.
- Deterministic behavior only; no network access.

## Non-Goals

- No changes to orchestrator runtime behavior.
- No automatic hook installation.
