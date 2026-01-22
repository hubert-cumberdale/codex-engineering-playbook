# Spec

## Goal

Integrate the deterministic review runner into CI and document its governance role.

## Context

The review runner from Task Pack 1 provides objective, deterministic checks for Tier 1 documents
and Task Pack structure. CI needs to run this same runner in strict mode, and Tier 1 governance
must explicitly document how the review system is enforced.

## Requirements

- Add a GitHub Actions workflow at `.github/workflows/review-checks.yml` that:
  - Triggers on `pull_request` and `workflow_dispatch`.
  - Runs `python -m tools.review.run_review --mode strict --report-path review_report.json`.
  - Uploads `review_report.json` as an artifact on both success and failure.
- CI blocks only on objective violations (exit code 2) and fails on runner errors (exit code 1).
- Update `docs/GOVERNANCE.md` to document:
  - Purpose of the deterministic review system.
  - Objective checks performed (high-level).
  - Local vs CI enforcement model.
  - No AI/LLM or heuristic inference.
  - JSON report as the source of truth.

## Non-Goals

- No changes to orchestrator runtime behavior.
- No new checks beyond the existing deterministic runner.
- No network access during review execution.
