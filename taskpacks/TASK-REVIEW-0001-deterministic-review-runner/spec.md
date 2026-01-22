# Spec

## Goal

Add a deterministic, repo-wide review runner that performs objective checks and writes a stable JSON report.

## Context

The repository needs a non-AI review runner that can be executed locally and in CI to validate Tier 1
documentation presence and Task Pack structure without relying on heuristics or network access.

## Requirements

- Provide `tools/review/run_review.py` with `--mode` and `--report-path` CLI options.
- Run deterministic checks for Tier 1 document presence and Task Pack required files.
- Emit a stable JSON report with sorted keys and predictable violation entries.
- Exit with code 0 on success, 2 on objective violations, 1 on runner errors.

## Non-Goals

- No changes to orchestrator runtime behavior.
- No new AI or heuristic-based checks.
- No network access or background execution.
