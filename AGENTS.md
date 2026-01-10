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
