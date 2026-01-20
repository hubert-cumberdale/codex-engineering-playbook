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

### CI (reference execution)
CI is a repeatable runner for the same command-based acceptance defined in `acceptance.yml`.


- Orchestrator executes validation/build commands
- Headless or scripted checks are run
- Logs and artifacts are collected

Manual playtesting is not part of this process.

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
- `artifacts/<taskpack-id>/` (exports, logs, or validation outputs)

Optional supporting artifacts:
- `artifacts/<taskpack-id>/manifest.json` (recommended if multiple artifacts exist)

If expected snapshots are used:
- `expected/report.md`

Artifacts must allow reviewers to evaluate success **without executing the task pack**.
Prefer deterministic filenames and stable structure.

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
