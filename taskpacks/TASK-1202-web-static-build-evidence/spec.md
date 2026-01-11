# TASK-1202 — Static mini-site build + evidence

## Goal
Demonstrate a minimal “web build” workflow that:
- transforms markdown-ish content into a static HTML page
- verifies internal links
- emits evidence artifacts under `artifacts/`

## In scope
- A deterministic builder (`tools/build_site.py`)
- Link verification (`tools/verify_links.py`)
- Evidence outputs:
  - `artifacts/site/index.html`
  - `artifacts/build_manifest.json`
  - `artifacts/link_report.json`

## Out of scope
- No frameworks, no npm installs, no deployment
- No network calls
- No server process required

## Reviewer checklist

- [ ] Acceptance completed with no failures (`LINT_CHECK_OK`, build + link checks pass)
- [ ] `artifacts/site/index.html` exists and includes:
  - [ ] `<h2 id='about'>`
  - [ ] `<h2 id='evidence'>`
  - [ ] Internal links to `#about` and `#evidence`
- [ ] `artifacts/build_manifest.json` exists and includes:
  - [ ] `taskpack_id` = `TASK-1202-web-static-build-evidence`
  - [ ] sha256 hashes for content, template, and output
  - [ ] `index_html_path` = `artifacts/site/index.html`
- [ ] `artifacts/link_report.json` exists with:
  - [ ] `status` = `ok`
  - [ ] `missing_anchors` = `[]`
- [ ] No deployment, hosting, or network behavior is implied or required
