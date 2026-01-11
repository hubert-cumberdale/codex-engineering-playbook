# Runbook (local)

```bash
cd taskpacks/TASK-1202-web-static-build-evidence
python -m compileall -q tools
python tools/lint_check.py
python tools/build_site.py
python tools/verify_links.py
```

Expected evidence in artifacts/:
- site/index.html
- build_manifest.json
- link_report.json

## Expected output snapshots

### Console output (example)
- `LINT_CHECK_OK`
- `SITE_BUILT artifacts/site/index.html`
- `LINK_CHECK_OK`

### `artifacts/site/index.html` (anchor + link presence)
Confirm the output contains:
- `<h2 id='about'>About</h2>`
- `<h2 id='evidence'>Evidence</h2>`
- `<a href="#about">About</a>`
- `<a href="#evidence">Evidence</a>`

### `artifacts/build_manifest.json` (shape)
- `taskpack_id` = `TASK-1202-web-static-build-evidence`
- `inputs.content_md_sha256` (64 hex)
- `inputs.template_html_sha256` (64 hex)
- `outputs.index_html_sha256` (64 hex)
- `outputs.index_html_path` = `artifacts/site/index.html`

Example excerpt:
```json
{
  "taskpack_id": "TASK-1202-web-static-build-evidence",
  "inputs": {
    "content_md_sha256": "…",
    "template_html_sha256": "…"
  },
  "outputs": {
    "index_html_path": "artifacts/site/index.html",
    "index_html_sha256": "…"
  }
}
```

### `artifacts/link_report.json` (expected values)
- `status` = `ok`
- `missing_anchors` = `[]`

Example excerpt:
```json
{
  "checked_file": "artifacts/site/index.html",
  "hrefs": ["#about", "#evidence"],
  "missing_anchors": [],
  "status": "ok",
  "taskpack_id": "TASK-1202-web-static-build-evidence"
}
```