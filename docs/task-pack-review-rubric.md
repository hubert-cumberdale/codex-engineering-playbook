# Task Pack Review Rubric (v1.x)

> **Status:** Informational / Reviewer Guidance
> **Applies to:** Example Task Packs and contributor submissions
> **Does not:** Introduce new system behavior, validators, or requirements

---

## Purpose

This rubric standardizes **human review** of Task Packs by anchoring evaluation to:

* **Evidence artifacts**
* **Deterministic acceptance**
* **Explicit scope and constraints**

It is intentionally **orthogonal** to automated validation and orchestrator logic.

---

## How to Use This Rubric

Reviewers should:

1. Run acceptance locally (or inspect CI output)
2. Open the referenced artifacts
3. Check off rubric items relevant to the Task Pack’s pillar

> Passing automated acceptance does **not** imply the Task Pack is well-scoped or review-ready.
> This rubric covers what automation cannot.

---

## Universal Requirements (All Task Packs)

These apply to **every** Task Pack, regardless of pillar.

### 1. Contract Compliance

* [ ] Task Pack runs in isolation
* [ ] No changes to orchestrator logic or flags required
* [ ] No plugins required (plugins may exist but must be gated/optional)
* [ ] Acceptance uses **command-based `must` only**
* [ ] No network access required or implied
* [ ] No cloud mutations or deployment language

---

### 2. Structure & Documentation

* [ ] `task.yml` includes:

  * [ ] Stable ID
  * [ ] Clear title
  * [ ] Explicit constraints
* [ ] `spec.md` clearly states:

  * [ ] Goal
  * [ ] In-scope behavior
  * [ ] Out-of-scope behavior
* [ ] `risk.md` identifies at least one realistic risk with mitigation
* [ ] `runbook.md` documents:

  * [ ] How to run acceptance
  * [ ] What artifacts to expect

---

### 3. Acceptance & Determinism

* [ ] Acceptance completes without failure
* [ ] Acceptance is deterministic:

  * [ ] No timestamps in artifacts
  * [ ] Stable ordering
  * [ ] Fixed zip metadata (if applicable)
* [ ] Acceptance produces artifacts every run
* [ ] Artifacts are written only to `artifacts/`

---

### 4. Evidence Artifacts

* [ ] `artifacts/README.md` explains:

  * [ ] What artifacts exist
  * [ ] How they were produced
* [ ] At least one **machine-readable** evidence artifact exists (e.g. JSON)
* [ ] Evidence artifacts include:

  * [ ] Task Pack ID
  * [ ] Inputs referenced by path or hash
  * [ ] Outputs referenced by path or hash
* [ ] Artifacts support reviewer verification without re-running tools

---

## Pillar-Specific Checks

### Security Task Packs

Focus: **verification, auditability, and scope discipline**

* [ ] No real secrets, credentials, or sensitive data included
* [ ] Sample data is clearly synthetic
* [ ] Evidence demonstrates *what was validated*, not just that a script ran
* [ ] Hashes or counts are used instead of raw sensitive content
* [ ] Scope does not drift into product, agent, or runtime behavior

Typical evidence examples:

* Redaction counts
* Validation reports
* Integrity hashes

---

### Web Task Packs

Focus: **build correctness without deployment semantics**

* [ ] Outputs are static (files, bundles, reports)
* [ ] No hosting, serving, or deployment language
* [ ] Internal links or references are verified
* [ ] Build artifacts are traceable to inputs via hashes or manifests
* [ ] No framework installs or external tooling required

Typical evidence examples:

* Static HTML output
* Build manifest JSON
* Link integrity reports

---

### Game Task Packs

Focus: **content pipelines, not engine builds**

* [ ] Task Pack validates content or data, not engine binaries
* [ ] Rules are explicit and enforced (IDs, references, schema shape)
* [ ] Validation failures are actionable and human-readable
* [ ] Bundles are deterministic and inspectable
* [ ] No runtime, rendering, or platform assumptions

Typical evidence examples:

* Content validation reports
* Deterministic asset bundles
* Schema compliance summaries

---

## Common Review Smells (Reasons to Push Back)

* ❌ “Deploy”, “publish”, “host”, or “release” language
* ❌ Acceptance that only prints logs without producing artifacts
* ❌ Artifacts that cannot be interpreted without reading code
* ❌ Implicit reliance on network, credentials, or environment state
* ❌ Task Packs that try to showcase *the orchestrator* instead of the work

---

## What This Rubric Is *Not*

* ❌ A validator
* ❌ A CI gate
* ❌ A hard requirement for all future Task Packs
* ❌ A substitute for system documentation

It exists to:

* Improve example quality
* Speed up reviews
* Reinforce evidence-first thinking

---

## Versioning

* **v1.x** — Aligned with Codex Orchestrator v1.x contract
* Changes to this rubric **do not** imply system changes

---
