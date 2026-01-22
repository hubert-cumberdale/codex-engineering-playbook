# Runbook

## Purpose

Install and run the advisory pre-push review hook.

## Install

- `PYTHONPATH=. python -m tools.review.install_hook`

## Uninstall

- `PYTHONPATH=. python -m tools.review.uninstall_hook`

## Strict mode

- `CODEX_REVIEW_STRICT=1 .git/hooks/pre-push`

## Expected output

- Hook file installed at `.git/hooks/pre-push`.
- Advisory runs do not block pushes.
- Strict mode exits non-zero on objective violations.
