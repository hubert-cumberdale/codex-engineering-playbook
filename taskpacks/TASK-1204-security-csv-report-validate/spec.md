# TASK-1204 — CSV → coverage report → schema validation

## Goal
Demonstrate a realistic evidence-first pipeline:
1. Parse a small CSV dataset representing detection/control coverage for techniques
2. Generate a deterministic report artifact set (`report.json`, `report.md`)
3. Validate the report schema locally and write validation evidence

## In scope
- CSV parsing + normalization
- Deterministic report generation:
  - `artifacts/report.json`
  - `artifacts/report.md`
- Deterministic schema validation evidence:
  - `artifacts/schema_validation.json`
- Unit tests for parsing and summary logic

## Out of scope
- No network calls
- No external dependencies (no pandas/jsonschema)
- No deployment language or runtime services
- No orchestrator changes, plugins, or new validators

## Acceptance
See `acceptance.yml` (command-based and local).

## Reviewer checklist
- [ ] Acceptance completed with no failures (compile, lint, tests, generate, validate)
- [ ] `artifacts/report.json` exists and includes:
  - [ ] `taskpack_id` = `TASK-1204-security-csv-report-validate`
  - [ ] `source_csv.path` = `data/sample_coverage.csv`
  - [ ] `source_csv.sha256` (64-char hex)
  - [ ] `summary.total_rows` matches CSV row count
  - [ ] `summary.by_status` includes keys for `covered`, `partial`, `missing`
- [ ] `artifacts/report.md` exists and includes:
  - [ ] A summary section with counts by status
  - [ ] A technique table with deterministic ordering
- [ ] `artifacts/schema_validation.json` exists and shows:
  - [ ] `status` = `ok`
  - [ ] `errors` = `[]`
- [ ] No secrets or real credentials appear in inputs or artifacts
- [ ] Task Pack runs in isolation without network access

> “This Task Pack is an example and should remain validator-clean.”