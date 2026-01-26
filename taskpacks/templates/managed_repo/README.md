# Managed Repo Task Pack Template — Walkthrough

This document explains how to use the **managed repo Task Pack template** to create
a scoped, auditable change in a managed repository workspace.

This is a **walkthrough**, not a system definition.
Authoritative system behavior and guarantees are defined under `/docs`.

---

## What this template is for

Use the managed repo Task Pack template when you need to:

- work in a managed workspace registered by the orchestrator,
- follow target repo governance and work-in-progress rules,
- run deterministic, local acceptance commands,
- produce reviewable evidence or artifacts when required.

---

## Template structure

A managed repo Task Pack follows the standard structure:

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
- the managed workspace key or path,
- explicit constraints and scope.

If a Task Pack does not declare network access, **none is assumed**.

---

## spec.md — Defining the work

`spec.md` answers:
- *What is changing?*
- *What does success mean?*
- *What is explicitly out of scope?*

Avoid qualitative language and keep the scope tight.

---

## acceptance.yml — Command-based acceptance

Acceptance is **command-based and local**.

Typical managed repo acceptance includes:
- format checks
- linting
- tests

Acceptance commands:

* must be deterministic,
* must fail fast,
* must not rely on implicit network access.

---

## risk.md — Declaring known risks

`risk.md` documents:
- known limitations,
- assumptions,
- areas of non-coverage.

This is not a threat model; it is scoped risk disclosure.

---

## runbook.md — Human execution notes

`runbook.md` provides:
- how to run the Task Pack locally,
- prerequisites (tools, versions),
- troubleshooting tips.

The runbook must not redefine acceptance or override constraints.

---

## How this fits together

The managed repo template combines:

* **Task Pack contract** (task.yml, spec.md)
* **Command-based acceptance** (acceptance.yml)
* **Explicit risk and runbook context**

All while respecting managed repo governance and scope constraints.
