# Runbook (Game)

This runbook describes how to execute and validate this game development task pack.

---

## Preconditions

Before running this task pack:

- Engine and version are explicitly declared
- Tooling supports headless or scripted execution
- No network, telemetry, or live services are enabled
- No secrets or platform-specific credentials are required

This task pack must be deterministic.

---

## How to run

### Local (optional)
If running locally:

1. Install the declared engine/tool version.
2. Run the documented headless or validation command.
3. Observe logs or exported outputs.

### CI (authoritative)
The authoritative run occurs in GitHub Actions:

- Orchestrator executes validation/build commands
- Headless or scripted checks are run
- Logs and artifacts are collected

Manual playtesting is not part of this process.

---

## Expected outputs

Outputs may include:
- Build or export artifacts
- Validation logs
- Structured output confirming behavior

Artifacts must allow reviewers to assess correctness without running the game interactively.

---

## Acceptance verification

Acceptance is defined in `acceptance.yml` and typically includes:
- Successful headless build or validation
- Explicit engine/version declaration
- No reliance on subjective criteria

A task **fails** if:
- Validation cannot run deterministically
- Acceptance depends on manual playtesting
- Engine/version is ambiguous or implicit

---

## How to interpret failures

- **Validation failure:** Review logs for engine or script errors.
- **Acceptance failure:** Confirm criteria are objective and machine-checkable.
- **Flaky behavior:** Investigate sources of nondeterminism (timing, randomness).

If deterministic validation is not possible, the task does not belong in this system.

---

## Review guidance

Reviewers should verify:
- Deterministic signals exist and are meaningful
- Engine/tool versions are pinned
- Scope is architectural or systemic, not experiential
- Artifacts are sufficient to evaluate success

If success is defined by “feel,” “fun,” or aesthetics, move the work outside this system.
