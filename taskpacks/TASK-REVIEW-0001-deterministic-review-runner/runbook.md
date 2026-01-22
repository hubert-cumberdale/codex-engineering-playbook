# Runbook

## Purpose

Run the deterministic review runner and capture a JSON report of objective checks.

## Commands

- Advisory mode:
  - `python tools/review/run_review.py --mode advisory --report-path artifacts/review-report.json`
- Strict mode:
  - `python tools/review/run_review.py --mode strict --report-path artifacts/review-report.json`

## Expected outputs

- A JSON report written to the path provided via `--report-path`.
- Exit code `0` when no violations are present; `2` when violations exist; `1` on runner error.

## Troubleshooting

- If a Tier 1 doc is reported missing, verify the file exists under `/docs`.
- If a Task Pack file is reported missing, ensure required files exist under the taskpack directory.
