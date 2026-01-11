# Runbook (local)

## Run
```bash
cd taskpacks/TASK-1204-security-csv-report-validate
python -m compileall -q src tests tools
python tools/lint_check.py
python -m unittest discover -s tests -p "test_*.py" -q
python tools/generate_report.py
python tools/validate_report.py
```

## Expected artifacts
- `artifacts/report.json`
- `artifacts/report.md`
- `artifacts/schema_validation.json`

## Expected output snapshots
### Console output (example)
- `LINT_CHECK_OK`
- `REPORT_WRITTEN artifacts/report.json artifacts/report.md`
- `SCHEMA_VALIDATION_OK artifacts/schema_validation.json`

### `artifacts/schema_validation.json` (expected shape)
- `status = ok`
`errors = []`

Example excerpt:
```json
{
  "errors": [],
  "status": "ok",
  "taskpack_id": "TASK-1204-security-csv-report-validate"
}
```

Notes:
- This Task Pack is local-only and deterministic (no timestamps, no network).

---