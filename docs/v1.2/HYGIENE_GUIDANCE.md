# v1.2 Hygiene Guidance (Tier-2, Advisory)

This document is **Tier-2 (informational)**.
It provides recommended authoring patterns for Task Packs to reduce contributor footguns and improve reviewability.

It does **not**:
- change orchestrator behavior
- add validators, flags, or enforcement
- modify acceptance expectations (still command-based and local)

## Goals
- Default new Task Packs to **deterministic, reviewable, evidence-first** behavior.
- Make the **review surface** obvious (primary evidence + supporting artifacts).

---

## Python import path rules (when applicable)

### Recommended patterns
- Prefer module execution:
  - `python -m package.module`
- Prefer an explicit import posture in acceptance/runbooks:
  - `PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v`

### Avoid
- Running scripts directly when they depend on implicit import paths:
  - `python tools/some_script.py`
- Ad-hoc `sys.path.append(...)` in production code.
  - If unavoidable in tests, document why and keep it local to tests.

---

## Explicit unittest discovery (when using unittest)

Always run tests with explicit discovery:
- `python -m unittest discover -s tests -p "test_*.py" -v`

This prevents environment-dependent discovery behavior.

---

## Deterministic artifact rules

Recommended defaults:
- Write artifacts under a single stable directory:
  - `artifacts/<taskpack-id>/`
- Use stable filenames (no timestamps in filenames):
  - `report.md`, `results.json`, `summary.txt`, `manifest.json`
- If timestamps are needed, put them **inside** the artifact content, not in the path.
- Normalize ordering:
  - sort rows/IDs; stable JSON key ordering when feasible; consistent line endings.

---

## Optional multi-artifact manifest pattern

If a Task Pack produces more than one artifact, consider adding:
- `artifacts/<taskpack-id>/manifest.json`

Example structure:
```json
{
  "taskpack_id": "TASK-XXXX",
  "primary_evidence": "report.md",
  "artifacts": [
    {"path": "report.md", "purpose": "Human-readable evidence summary"},
    {"path": "results.json", "purpose": "Machine-readable results"},
    {"path": "logs.txt", "purpose": "Supporting logs (optional)"}
  ]
}
```

This is **optional** and intended to make review surfaces obvious.

---

## Expected output snapshots (goldens) in runbooks

If you generate report-like outputs, consider committing an expected snapshot:

* `expected/report.md` (or similar)

Runbooks should include:

* expected output list (primary evidence + optional supporting artifacts)
* regeneration steps
* what reviewers should diff

Example runbook section:

```md
## Expected Outputs (Review Surface)

Primary evidence:
- artifacts/<taskpack-id>/report.md

If using expected snapshots:
- expected/report.md

### Regenerating expected outputs
1) Run: python tools/generate_report.py --out artifacts/<taskpack-id>/report.md
2) Update snapshot: cp artifacts/<taskpack-id>/report.md expected/report.md
3) Review: git diff expected/report.md
```
