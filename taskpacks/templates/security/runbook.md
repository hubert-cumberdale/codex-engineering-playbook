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

### CI (authoritative)
The authoritative execution is via GitHub Actions:

- Triggered by `workflow_dispatch`
- Orchestrator runs phases, acceptance checks, and produces artifacts
- Results are attached to the run as downloadable artifacts

---

## Expected outputs

This task pack is expected to produce:

- One or more artifacts under `artifacts/`
- Artifacts may include:
  - Reports
  - Logs
  - Structured outputs (JSON/YAML/CSV)
  - Findings summaries

Artifacts are treated as **primary evidence**.

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
