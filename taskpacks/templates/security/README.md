# Security Task Pack Template — Walkthrough

This document explains how to use the **security Task Pack template** to create
a contract-safe, auditable security engineering change using the Codex Orchestrator.

This is a **walkthrough**, not a system definition.
Authoritative system behavior and guarantees are defined under `/docs`.

---

## What this template is for

Use the security Task Pack template when you need to:

- validate security controls, detections, or posture,
- simulate or assess security scenarios (e.g., BAS, CTEM, ASM),
- analyze artifacts or evidence (e.g., DFIR-style workflows),
- produce reviewable security evidence in CI.

This template supports **security engineering**, not live operations.

---

## What this template is NOT for

This template does **not** support:
- live attack execution against external targets,
- persistent agents or background monitoring,
- production deployments or runtime enforcement,
- implicit network or cloud access.

All security work must remain:
- scoped,
- explicit,
- auditable,
- and runnable in isolation.

---

## Template structure

A security Task Pack follows the standard structure:

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

Each file has a distinct responsibility and must remain self-contained.

---

## task.yml — Declaring intent and constraints

`task.yml` defines:
- the identity of the Task Pack,
- the category of security work,
- execution constraints.

Security Task Packs should be explicit about:
- whether network access is required,
- whether cloud APIs are accessed,
- whether tools are simulated or stubbed.

If a security Task Pack does not declare network access, **none is assumed**.

---

## spec.md — Defining the security contract

`spec.md` answers:
- *What security question is being asked?*
- *What is being validated or analyzed?*
- *What constitutes success?*
- *What is explicitly out of scope?*

Examples of valid security contracts:
- “Validate that detection logic flags known input patterns.”
- “Confirm that a security report can be generated deterministically.”
- “Prove that a simulated control check produces expected output.”

Avoid:
- qualitative language (“strong”, “robust”, “secure”),
- implied threat coverage beyond what is tested.

---

## acceptance.yml — Command-based security validation

Security acceptance is **command-based and local**.

Common patterns include:
- static analysis or linting
- rule or configuration validation
- test harness execution
- report generation

Example pattern (conceptual):

```yaml
version: 1
must:
  - name: validate
    cmd: python -m pytest -q
  - name: report
    cmd: python scripts/generate_report.py
```

Rules:

* Commands must be deterministic.
* Acceptance must not rely on hidden credentials.
* External services require explicit constraints.

See also:

* **Skill: security-ci-security-gates**
* **Skill: web-acceptance-contracts** (shared acceptance principles)

---

## artifacts/ — Evidence-first security output

Security Task Packs must treat artifacts as **primary evidence**.

Typical artifacts include:

* validation summaries
* generated reports
* structured result files (JSON, CSV, TXT)

Example layout:

```
artifacts/
├── README.md
└── validation-summary.txt
```

### artifacts/README.md

Explain:

* what security contract is being proven,
* what evidence files exist,
* what is *not* validated.

### Evidence files

Evidence should be:

* small and textual,
* reviewable in PRs,
* stable across runs.

Avoid:

* raw logs without context,
* large binary outputs,
* artifacts that embed secrets.

---

## risk.md — Declaring known limitations

`risk.md` documents:

* assumptions made by the Task Pack,
* blind spots or exclusions,
* areas intentionally not validated.

Examples:

* “Does not validate production deployment.”
* “Simulated inputs only; no live traffic.”
* “Detection logic tested in isolation.”

This is **not** a threat model; it is scoped disclosure.

---

## runbook.md — Human execution notes

`runbook.md` provides:

* prerequisites (tools, versions),
* how to run the Task Pack locally,
* common failure modes and fixes.

The runbook must not:

* override acceptance,
* weaken constraints,
* introduce new execution paths.

---

## How this fits together

The security template combines:

* explicit security intent,
* deterministic acceptance,
* evidence-first artifacts,
* declared risks and assumptions,

while preserving:

* safety-by-default execution,
* auditability,
* and platform neutrality.

Security Task Packs are **peers** to web and game Task Packs, not special cases.

---

## See also

* **Skill: security-ci-security-gates**
* **Skill: web-acceptance-contracts** — shared acceptance principles
* **TASK-0100-security-artifact-contract-check** — canonical security canary

---
