# Runbook (local)

```bash
cd taskpacks/TASK-1203-game-content-validate-bundle
python -m compileall -q tools
python tools/lint_check.py
python tools/validate_content.py
python tools/bundle_content.py
```

Expected evidence:
- artifacts/validation_report.json
- artifacts/content_bundle.zip

## Expected output snapshots

### Console output (example)
- `LINT_CHECK_OK`
- `CONTENT_VALIDATION_OK`
- `BUNDLE_WRITTEN artifacts/content_bundle.zip`

### `artifacts/validation_report.json` (expected values)
- `status` = `ok`
- `event_count` = `2`
- `unique_ids` = `2`
- `broken_links` = `[]`

Example excerpt:
```json
{
  "broken_links": [],
  "event_count": 2,
  "file": "content/events.json",
  "status": "ok",
  "taskpack_id": "TASK-1203-game-content-validate-bundle",
  "unique_ids": 2
}
```

### `artifacts/content_bundle.zip` (contents)
The zip should include (paths are relative to repo root):
- content/events.json
- content/schema_notes.md

To inspect locally (optional, not required by acceptance):

```bash
python -c "import zipfile; z=zipfile.ZipFile('artifacts/content_bundle.zip'); print('\n'.join(z.namelist()))"
```

## Notes:
- Zip entry timestamps are fixed for determinism.
- This Task Pack validates and bundles content only (no engine build).

---