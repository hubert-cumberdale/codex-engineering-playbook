# Task Pack Examples (v1.x)

These example Task Packs demonstrate contract-aligned, evidence-first workflows.
They are runnable in isolation and require no plugins.

## Examples

### Security — TASK-1201-security-redaction-audit
Path: `taskpacks/TASK-1201-security-redaction-audit`

Evidence:
- `artifacts/evidence.json`
- `artifacts/redacted_sample.txt`

Run:
```bash
cd taskpacks/TASK-1201-security-redaction-audit
python -m compileall -q src tests tools
python tools/lint_check.py
python -m unittest discover -s tests -p "test_*.py" -q
python tools/make_evidence.py
```

### Web — TASK-1202-web-static-build-evidence

Path: `taskpacks/TASK-1202-web-static-build-evidence`

Evidence:

* `artifacts/build_manifest.json`
* `artifacts/link_report.json`
* `artifacts/site/index.html`

Run:

```bash
cd taskpacks/TASK-1202-web-static-build-evidence
python -m compileall -q tools
python tools/lint_check.py
python tools/build_site.py
python tools/verify_links.py
```

### Game — TASK-1203-game-content-validate-bundle

Path: `taskpacks/TASK-1203-game-content-validate-bundle`

Evidence:

* `artifacts/validation_report.json`
* `artifacts/content_bundle.zip`

Run:

```bash
cd taskpacks/TASK-1203-game-content-validate-bundle
python -m compileall -q tools
python tools/lint_check.py
python tools/validate_content.py
python tools/bundle_content.py
```

## Review standard

* Tier-1 Documentation Checklist: `docs/DOC_CHECKLIST_TIER1.md`
* Task Pack Review Rubric (v1.x): `docs/task-pack-review-rubric.md`

---

### Security — TASK-1204-security-csv-report-validate
Path: `taskpacks/TASK-1204-security-csv-report-validate`

Demonstrates a multi-step, evidence-first pipeline:
CSV ingestion → report generation → schema validation.

Evidence:
- `artifacts/report.json`
- `artifacts/report.md`
- `artifacts/schema_validation.json`

Run:
```bash
cd taskpacks/TASK-1204-security-csv-report-validate
python -m compileall -q src tests tools
python tools/lint_check.py
python -m unittest discover -s tests -p "test_*.py" -q
python tools/generate_report.py
python tools/validate_report.py
```