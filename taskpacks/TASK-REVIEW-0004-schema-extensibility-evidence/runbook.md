# Runbook

## Run Tests
```bash
PYTHONPATH=. python -m pytest -q
```

## Generate Review Report
```bash
PYTHONPATH=. python -m tools.review.run_review --mode advisory --report-path /tmp/review_report.json
```

## Collect Review Evidence (Orchestrator, Opt-In)
```bash
ORCH_COLLECT_REVIEW=1 TASKPACK_PATH=taskpacks/TASK-REVIEW-0004-schema-extensibility-evidence \
python tools/orchestrator/orchestrate.py
```
