# Runbook (Managed Repo)

This runbook describes how to execute and validate this managed repo task pack.

---

## Preconditions

Before running this task pack:

- Working tree is clean
- Correct language/runtime versions are available
- No production credentials or secrets are present
- Network and cloud mutation are disabled unless explicitly declared

Read and follow the target repo contracts:
- `docs/GOVERNANCE.md`
- `docs/CURRENT_WORK.md`

---

## How to run

### Local (optional)
If running locally:

1. Install dependencies as defined by the project.
2. Run the commands defined in `acceptance.yml`.
3. Confirm outputs match expectations.

### CI (reference execution)
CI is a repeatable runner for the same command-based acceptance defined in `acceptance.yml`.

- Orchestrator executes the task
- Acceptance commands run
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

Primary evidence (if produced):
- `artifacts/<taskpack-id>/`

If expected snapshots are used:
- `expected/`

Artifacts must allow reviewers to evaluate success **without executing the task pack**.
Prefer deterministic filenames and stable structure.

---

## Acceptance verification

Acceptance is defined in `acceptance.yml` and typically includes:
- Successful format/lint/test execution
- No deployment or cloud mutation behavior introduced
- File changes limited to declared scope

A task **fails** if:
- Acceptance commands fail
- Deployment or cloud mutation logic is detected
- Scope exceeds what is declared

---

## How to interpret failures

- **Format/lint/test failure:** Inspect logs for errors.
- **Acceptance failure:** Review forbidden patterns or scope violations.
- **Unexpected diffs:** Ensure changes align with `spec.md`.

If the task is too large or unclear, split it into smaller task packs.
