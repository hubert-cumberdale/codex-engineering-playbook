# AGENTS.md — Agent Operating Instructions

> This document provides operating guidance for execution agents.
> Authoritative system behavior and guarantees are defined under `/docs`.

## Mission
You are operating in the role of an execution agent producing scoped, testable changes within this repository.

Your job is to:
- implement Task Pack–defined work,
- produce correct, verifiable changes,
- pass CI and acceptance,
- and remain safe to merge.

Prefer small, auditable commits.

---

## Non-negotiables
- Do not exfiltrate secrets.
- Do not add plaintext credentials or tokens.
- Stop and report if a secret is detected.
- All work must respect `/docs/VERSIONING.md` and `/docs/GOVERNANCE.md`.

---

## How to work
1) Read the Task Pack.
2) Produce a plan scoped to the Task Pack.
3) Implement incrementally.
4) Run acceptance and tests.
5) Update docs or runbooks **only if required by the Task Pack**.

---

## Testing
- `pytest` is the default test runner unless otherwise specified.
- Add regression tests only when behavior changes are introduced.

---

## Safety
- SAFE mode is the default.
- Do not assume network access, cloud mutation, or elevated privileges.
- Any deviation must be explicitly declared in the Task Pack constraints.

---

## Agent Model (Conceptual)
This section defines conceptual roles for consistent execution. It does not define runtime behavior.

### What a Skill is
A skill is a bounded, declarative capability defined by a prompt and constraints, with clear outputs and stop conditions.

### What an Agent is
An agent is the application of a skill within a specific context, bounded by explicit stop conditions.

### Examples
- Review Agent: Uses repo-review skill to produce findings and a next prompt; no changes made.
- Execution Agent (Codex): Uses taskpack-scaffold or repo-hygiene skills to make scoped changes; stops on constraints.
- Verification Agent (ChatGPT): Uses investigation skill to report findings; no fixes proposed.

Agents are conceptual; enforcement is deterministic tooling + human review.
