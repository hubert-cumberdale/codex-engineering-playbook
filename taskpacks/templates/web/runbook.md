# Runbook (Web)

This runbook describes how to execute and validate this web development task pack.

---

## Preconditions

Before running this task pack:

- Working tree is clean
- Correct language/runtime versions are available
- No production credentials or secrets are present
- Deployment and infrastructure mutation are disabled unless explicitly declared

This task pack must not assume a live environment.

---

## How to run

### Local (optional)
If running locally:

1. Install dependencies as defined by the project (e.g., `npm install`, `pip install`).
2. Run the build and/or test commands defined in the task.
3. Confirm outputs match expectations.

### CI (reference execution)
CI is a repeatable runner for the same command-based acceptance defined in `acceptance.yml`.

- Orchestrator executes the task
- Build/test commands run
- Acceptance checks are evaluated
- Logs and artifacts are uploaded

---

## Hygiene guidance (v1.2, advisory)

This section is **informational (Tier-2)** and does not change acceptance behavior.

### Python import path rules (when applicable)
- Prefer an explicit import posture for parity between local and CI execution.
  - Example: `PYTHONPATH=. ...` or `PYTHONPATH=src ...`
- Prefer module execution where applicable:
  - `python -m package.module`

### Explicit unittest discovery (when using unittest)
If this task pack uses `unittest`, use explicit discovery:
- `PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py" -v`

### Deterministic artifact rules
- Write evidence to stable paths under `artifacts/`.
- Filenames must be deterministic; avoid timestamps in filenames.
- If timestamps are useful, include them inside artifact content.

---

## Expected outputs

### Expected Outputs (Review Surface)

Primary evidence (if produced):
- `artifacts/<taskpack-id>/build/`
- `artifacts/<taskpack-id>/report.md`

Optional supporting artifacts:
- `artifacts/<taskpack-id>/results.json`
- `artifacts/<taskpack-id>/manifest.json` (recommended if multiple artifacts exist)

If expected snapshots are used:
- `expected/report.md`

Artifacts must allow reviewers to evaluate success **without executing the task pack**.
Prefer deterministic filenames and stable structure.

---

## Acceptance verification

Acceptance is defined in `acceptance.yml` and typically includes:
- Successful build or test execution
- No deployment or production logic introduced
- File changes limited to declared scope

A task **fails** if:
- Build/test commands fail
- Deployment logic is detected
- Scope exceeds what is declared

---

## How to interpret failures

- **Build/test failure:** Inspect logs for compilation or test errors.
- **Acceptance failure:** Review forbidden patterns or scope violations.
- **Unexpected diffs:** Ensure changes align with `spec.md`.

If the task is too large or unclear, split it into smaller task packs.

---

## Review guidance

Reviewers should verify:
- The change is incremental and scoped
- Contracts (APIs, schemas) are respected or explicitly updated
- No deployment or environment-specific behavior is introduced
- Acceptance criteria objectively reflect success

If success requires a manual environment or production data, the task is out of scope.
