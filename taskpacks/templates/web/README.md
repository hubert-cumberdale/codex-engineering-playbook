# Web Task Pack Template — Walkthrough

This document explains how to use the **web Task Pack template** to create
a contract-safe, CI-verifiable web change using the Codex Orchestrator.

It is a **walkthrough**, not a system definition.
Authoritative system behavior is defined under `/docs`.

---

## What this template is for

Use the web Task Pack template when you need to:

- modify web application or service code,
- validate changes with local, command-based acceptance,
- prove a build or packaging contract with evidence,
- remain within v1 safety and reproducibility guarantees.

This template does **not** assume a specific web framework.

---

## Template structure

A web Task Pack follows the standard structure:

```txt
taskpacks/<TASK-ID>-<slug>/
├── task.yml
├── spec.md
├── acceptance.yml
├── risk.md
├── runbook.md
└── artifacts/
└── README.md
```

Each file serves a specific purpose and must remain self-contained.

---

## task.yml — Declaring intent and constraints

`task.yml` defines:
- the identity of the Task Pack,
- high-level intent,
- constraints that govern execution.

Key expectations:
- Constraints are explicit.
- Network access is **not assumed**.
- No deployment or runtime mutation is implied.

Example intent (conceptual):
- “Validate that the web project builds deterministically.”

---

## spec.md — Defining the work

`spec.md` answers:
- *What is changing?*
- *What does success mean?*
- *What is explicitly out of scope?*

For web Task Packs:
- Describe the code or configuration being modified.
- Describe what contract is being validated (e.g., build succeeds).
- Avoid qualitative language (“looks good”, “modern”, “fast”).

---

## acceptance.yml — Command-based acceptance

Acceptance is **command-based and local**.

Typical web acceptance includes:
- format checks
- linting
- tests
- build or package step

Example pattern (simplified):

```yaml
version: 1
must:
  - name: format
    cmd: npm run format:check
  - name: lint
    cmd: npm run lint
  - name: test
    cmd: npm test -- --ci
  - name: build
    cmd: npm run build
```

Acceptance commands:

* must be deterministic,
* must fail fast,
* must not rely on implicit network access.

See also:

* **Skill: web-acceptance-contracts**

---

## artifacts/ — Evidence-first output

If the Task Pack claims a build contract, it must emit evidence.

Artifacts are:

* primary proof of success,
* small and reviewable,
* validated by acceptance or validators.

Typical layout:

```
artifacts/
├── README.md
└── build-contract.txt
```

### artifacts/README.md

Explain:

* what contract is being proven,
* what evidence files exist,
* what is *not* being validated (e.g., deployment).

### build-contract.txt

A short, textual summary of:

* build command executed,
* tool versions (when easy),
* output summary,
* success status.

Avoid:

* full logs,
* large binary outputs,
* non-deterministic hashes.

See also:

* **Skill: web-build-artifact-evidence**

---

## risk.md — Declaring known risks

`risk.md` documents:

* known limitations,
* assumptions,
* areas of non-coverage.

Examples:

* “Does not validate deployment.”
* “Build relies on local toolchain versions.”

This is not a threat model; it is scoped risk disclosure.

---

## runbook.md — Human execution notes

`runbook.md` provides:

* how to run the Task Pack locally,
* prerequisites (tools, versions),
* troubleshooting tips.

The runbook must not:

* redefine acceptance,
* override constraints,
* introduce new execution paths.

---

## How this fits together

The web template combines:

* **Task Pack contract** (task.yml, spec.md)
* **Command-based acceptance** (acceptance.yml)
* **Evidence-first artifacts** (artifacts/)
* **Explicit risk and runbook context**

All without:

* changing orchestrator behavior,
* enabling plugins by default,
* assuming deployment or runtime environments.

---

## See also

* **Skill: web-acceptance-contracts**
* **Skill: web-build-artifact-evidence**
* **TASK-0101-web-build-contract-check** — canonical web canary Task Pack

````
