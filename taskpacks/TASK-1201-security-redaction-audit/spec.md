# TASK-1201 — Redaction utility + audit evidence pack

## Goal
Provide a tiny, deterministic redaction utility that:
- redacts email addresses, IPv4 addresses, and long tokens (≥ 20 chars)
- emits an evidence pack proving what was redacted (counts + sha256)

## In scope
- A pure-stdlib Python redaction module
- Unit tests (stdlib `unittest`)
- Evidence generation into `artifacts/`:
  - `redacted_sample.txt`
  - `evidence.json` including:
    - sha256 of input + output
    - redaction counts by type
    - tool/version metadata (python version)

## Out of scope
- No network calls
- No dependency installs
- No deployment or runtime service behavior

## Acceptance
See `acceptance.yml` (command-based, local).

## Reviewer checklist

- [ ] Acceptance completed with no failures (`LINT_CHECK_OK`, tests pass, evidence written)
- [ ] `artifacts/evidence.json` exists and includes:
  - [ ] `taskpack_id` = `TASK-1201-security-redaction-audit`
  - [ ] `inputs.input_sha256` (64-char hex)
  - [ ] `outputs.output_sha256` (64-char hex)
  - [ ] `redaction_counts` with keys `email`, `ipv4`, `token`
- [ ] `artifacts/redacted_sample.txt` contains redaction markers:
  - [ ] `[REDACTED_EMAIL]`
  - [ ] `[REDACTED_IPV4]`
  - [ ] `[REDACTED_TOKEN]`
- [ ] No raw secrets or real credentials appear in artifacts or source files
- [ ] Task Pack runs in isolation with no network access

> “This Task Pack is an example and should remain validator-clean.”