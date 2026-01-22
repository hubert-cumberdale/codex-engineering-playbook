# Deterministic Review Runner

This folder contains the deterministic review runner used to enforce objective, repo-wide checks.
The runner is **non-AI**, **no-network**, and purely **rule-based**.

## What it does
- Runs a fixed set of objective checks (no heuristics).
- Produces a machine-readable JSON report.
- Is advisory by default for local runs.
- Can be strict (CI-blocking) when requested.

## CLI usage
Advisory mode (default):

```bash
python -m tools.review.run_review --mode advisory
```

Strict mode (fails on violations):

```bash
python -m tools.review.run_review --mode strict
```

Override report path:

```bash
python -m tools.review.run_review --report-path .review/review_report.json
```

Override repo root (useful for tests):

```bash
python -m tools.review.run_review --repo-root /path/to/repo
```

## Report output
- Always writes `review_report.json`.
- Default location:
  - `.orchestrator_logs/review_report.json` if `.orchestrator_logs/` exists.
  - Otherwise `./review_report.json`.
- Keys are deterministically ordered for stable diffs.

## Exit codes
- `0` = pass (no violations) or advisory mode with violations.
- `2` = violations found in strict mode.
- `1` = runner error (unexpected exception).

## Checks included
- **Repo layout:** required Tier-1 docs and `.codex/library` presence.
- **Taskpack contracts:** required files under each `taskpacks/TASK-*/` directory.

Check implementations live under `tools/review/checks/`.
