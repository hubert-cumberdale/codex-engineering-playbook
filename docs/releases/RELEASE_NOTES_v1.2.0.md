# Release Notes — v1.2.0

## Summary
v1.2.0 adds a deterministic, non-AI review system with a versioned JSON report schema, opt-in local enforcement via a pre-push hook, and CI enforcement on objective violations. Orchestrator evidence collection is available as an opt-in, non-enforcing feature.

## What Changed
- Added a deterministic review runner (`python -m tools.review.run_review`) with a versioned JSON report schema and stable violation ordering.
- Added an opt-in pre-push hook that runs the review runner in advisory mode; strict mode is opt-in via `CODEX_REVIEW_STRICT=1`.
- Added a CI workflow that runs the review runner in strict mode and blocks only on objective violations (exit code 2).
- Documented the deterministic review system and schema extension guidance in Tier-1/Tier-2 docs.
- Added opt-in orchestrator evidence collection via `ORCH_COLLECT_REVIEW=1` (non-enforcing).

## How to Run (Offline)
Local advisory run:

```bash
PYTHONPATH=. python -m tools.review.run_review --mode advisory --report-path review_report.json
```

Install the opt-in pre-push hook:

```bash
./scripts/install-pre-push-hook.sh
```

## Compatibility / Breaking Changes
None. Default behavior remains unchanged; enforcement is opt-in locally and strict only in CI.

## Evidence / Artifacts
- `review_report.json` (JSON report artifact).
- `schema_version` = 1 in the report header.
