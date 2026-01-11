# Runbook (Security)

This runbook describes how to execute, validate, and review this security task pack.

---

## Preconditions

Before running this task pack:

- You are on a clean working tree
- You are on the correct base branch (`main` or a task branch created by the orchestrator)
- No secrets are present in the environment
- Network access and cloud mutation are disabled unless explicitly declared in `task.yml`

This task pack must be runnable in isolation.

---

## How to run

### Local (optional)
If running locally with Codex CLI:

1. Ensure dependencies declared in the repo are installed.
2. Run the task pack using the orchestrator entrypoint or documented commands.
3. Observe generated artifacts under `artifacts/`.

### CI (reference execution)
CI is a repeatable runner for the same command-based acceptance defined in `acceptance.yml`.

- Triggered by `workflow_dispatch`
- Orchestrator runs phases, acceptance checks, and produces artifacts
- Results are visible via logs and produced artifacts

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

## Expected Outputs (Review Surface)

Primary evidence:
- `artifacts/<taskpack-id>/` (primary evidence directory)

Optional supporting artifacts:
- `artifacts/<taskpack-id>/manifest.json`  
  (recommended if multiple artifacts are produced)

If expected snapshots are used:
- `expected/report.md`

Artifacts must allow reviewers to evaluate success **without executing the task pack**.
Prefer deterministic filenames and stable structure.

---

## Acceptance verification

Acceptance is determined by `acceptance.yml`.

Typical checks include:
- Artifacts exist
- Outputs include explicit findings or results
- No unexpected file modifications occurred

A task **fails** if:
- Required artifacts are missing
- Acceptance checks fail
- Execution violates declared constraints

---

## How to interpret failures

- **Acceptance failure:** Review `acceptance.yml` and artifacts to determine which check failed.
- **Execution failure:** Review orchestrator logs and plugin output (if applicable).
- **Unexpected behavior:** Confirm constraints in `task.yml` were not violated.

If failures are unclear, tighten acceptance or split the task pack.

---

## Review guidance

Reviewers should verify:
- Scope matches `spec.md`
- Artifacts support the stated security objective
- Assumptions and limitations are explicit
- No unsafe behavior or scope creep occurred

If results cannot be verified via artifacts, the task pack is incomplete.
