# Runbook (local)

```bash
cd taskpacks/TASK-1290-platform-taskpack-hygiene-audit
python -m compileall -q tools
python tools/lint_check.py
python tools/hygiene_scan.py
```

## Expected artifacts
- `artifacts/hygiene_report.json`
- `artifacts/hygiene_report.md`

## Expected output snapshot
- `HYGIENE_SCAN_COMPLETE artifacts/hygiene_report.json`