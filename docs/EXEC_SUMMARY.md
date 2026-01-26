# Codex Orchestrator — Executive Summary (v1.3.0)

## What This Is
Codex Orchestrator is a fault-tolerant engineering system where **ChatGPT operates as the control plane** and **Codex (CLI + GitHub + Actions) operates as the execution plane**.

It is designed to deliver **repeatable, auditable, safety-first engineering outcomes**, with a primary focus on **security engineering, web development, and game development**.

---

## The Problem It Solves
Modern engineering workflows fail due to:
- Context rot
- Unsafe automation
- Over-autonomous agents
- Non-reproducible results
- Tribal knowledge embedded in long chats

Codex Orchestrator solves this by enforcing:
- Explicit work units
- Bounded autonomy
- Machine-checkable acceptance
- Mandatory evidence

---

## Core Design
### Control Plane vs Data Plane
- **ChatGPT (Control Plane)**  
  Owns strategy, task decomposition, acceptance criteria, and risk posture.

- **Codex Agents (Data Plane)**  
  Execute implementation, tests, commits, and PRs — within strict constraints.

This separation is intentional and enforced.

---

## Unit of Work: Task Packs
All work is expressed as **Task Packs**:
- Self-contained
- Runnable in isolation
- Reproducible
- Auditable

A task that cannot be represented as a Task Pack does not belong in the system.

---

## v2 Plugins (Solution Integration)
The orchestrator can optionally run a solution plugin declared in a taskpack (`task.yml: plugin:`).

- Enable: `ORCH_ENABLE_PLUGINS=1`
- Strict mode: `ORCH_PLUGINS_STRICT=1`
- Stable branch: `ORCH_BRANCH_NAME=codex/<task-id>`
- Base branch override: `BASE_BRANCH=main`

Artifacts include `plugin_result.json` and a manifest entry for auditability.

---

## Safety Model
Safety is **default-on**, not optional.
- No network access unless declared
- No cloud mutations unless declared
- Secret access is forbidden
- Circuit breakers prevent runaway behavior

Unsafe behavior fails fast and produces evidence.

---

## Execution Guarantees
Each orchestrator run produces:
- A manifest
- Phase logs
- A human-readable summary
 - Optional deterministic evidence artifacts (review report and evidence index)

Success and failure are equally auditable.

---

## Scope of v1.3.0
v1 provides:
- Stable execution pipeline
- Task Pack schema
- Safety model
- Circuit breakers
- Evidence guarantees
- Solution-agnostic architecture with solution plugins living under /solutions (e.g., security/web/game)
- Deterministic review runner (schema v1)
- Evidence index builder + query CLI (schema v1)

v1 explicitly does **not** include:
- Long-lived agents
- Cross-task memory
- Unbounded autonomy
- Implicit state
- Vendor lock-in

---

## Why This Matters
Codex Orchestrator enables:
- Secure autonomous iteration
- Engineering at scale without chaos
- Confidence in AI-assisted development
- Security validation as code

This is infrastructure for *serious* engineering work.

---

## Status
**v1.3.0 is production-stable and contract-locked.**

All future expansion must respect the v1 guarantees.
