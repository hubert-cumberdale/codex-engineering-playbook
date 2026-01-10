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

### CI (authoritative)
The authoritative run occurs in GitHub Actions:

- Orchestrator executes the task
- Build/test commands run
- Acceptance checks are evaluated
- Logs and artifacts are uploaded

---

## Expected outputs

Depending on the task, outputs may include:
- Build artifacts (`dist/`, `build/`)
- Test results or coverage reports
- Updated source or test files

Artifacts are optional unless required by acceptance.

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
