# Runbook

## Purpose

Validate documentation updates and release notes for the deterministic review system.

## Steps

1) Confirm the next minor version from git tags.
2) Review `docs/GOVERNANCE.md` for contract-safe language.
3) Run tests:

```bash
PYTHONPATH=. python -m pytest -q
```
