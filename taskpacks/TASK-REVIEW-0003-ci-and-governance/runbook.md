# Runbook

## Purpose

Run the deterministic review runner locally and understand CI enforcement behavior.

## Local run

- `PYTHONPATH=. python -m tools.review.run_review --mode strict --report-path review_report.json`

## CI behavior

- The `review-checks` workflow runs the same command in strict mode on pull requests.
- The JSON report artifact `review_report.json` is uploaded on success and failure.
- Exit code `2` indicates objective violations and blocks CI; exit code `1` indicates runner error.
