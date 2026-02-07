# ChatGPT Playbook
## Codex Engineering Playbook

This document defines **how ChatGPT is used** in the Codex Engineering Playbook.

Its purpose is to:
- Prevent context rot
- Enforce clean boundaries between thinking and execution
- Ensure decisions become durable artifacts
- Keep autonomy bounded and auditable

ChatGPT is part of the **control plane**, not a memory store.

---

## Core Principle

> **Chats are for thinking.  
> Repos are for memory.  
> Task Packs are for action.**

If something matters beyond the current discussion, it must be written to the repository.

---

## What ChatGPT Is Used For

ChatGPT is used to:

- Define system architecture and contracts
- Design schemas and abstractions
- Draft canonical documentation
- Decompose work into Task Packs
- Review results and PRs
- Reason about failures and next steps

ChatGPT **does not** execute code, persist state, or replace documentation.

---

## What ChatGPT Is *Not* Used For

ChatGPT is not:

- A long-term memory system
- A “forever chat”
- A replacement for Task Packs
- A substitute for release notes or governance
- An execution environment

If a chat outcome is not captured in the repo, it is considered **nonexistent**.

---

## Chat Types (Explicit Modes)

Each chat must have a **single primary intent**.

### 1. Governance & Architecture Chats
Used for:
- System contracts
- Versioning rules
- Governance decisions
- New abstractions (e.g. `security/solutions/bas_core`)

Characteristics:
- Low frequency
- High impact
- Output is documentation

Examples:
- `Codex Orchestrator v1 — Formalization`
- `Codex Orchestrator v2 — security/solutions/bas_core Design`

---

### 2. Task Pack Chats
Used for:
- Designing a specific Task Pack
- Clarifying scope and acceptance
- Reviewing Task Pack results

Characteristics:
- Short-lived
- Narrow scope
- Ends when Task Pack is defined or completed

**Naming convention**
[TASK-####] <short description>


Examples:
- `[TASK-0042] AttackIQ Assessment Template`
- `[TASK-0107] Orchestrator Artifact Upload Fix`

---

### 3. Debugging Chats
Used for:
- Investigating a failure
- Interpreting logs
- Deciding reroute / retry / abort

Characteristics:
- Evidence-driven
- Tactical
- Does not redefine architecture

Outputs:
- Diagnosis
- Recommended next Task Pack

---

## When to Start a New Chat (Hard Rules)

Start a new chat when **any** of the following are true:

### 🔴 Scope Change
Switching between:
- Architecture ↔ implementation
- Governance ↔ debugging
- One Task Pack ↔ another Task Pack
- Domains (security/web/game)

---

### 🔴 Task Pack Boundary
If work can be represented as a Task Pack, it gets:
- Its own chat
- Its own lifecycle
- Its own end condition

---

### 🔴 Context Saturation
Start a new chat when:
- You need to scroll significantly to reorient
- You reference earlier discussion repeatedly
- A new contributor wouldn’t reasonably read the whole chat

---

### 🔴 Version Boundary
When a MAJOR version is closed:
- Do not continue design in the same chat
- Start a new version-scoped chat

Example:
Codex Orchestrator v2 — Design

Start a new chat at each milestone (merge)

---

## Chat Lifecycle (Required)

Every chat should follow this lifecycle:

1. **Intent**
   - What are we here to decide or design?
2. **Output**
   - Concrete artifacts (docs, schemas, decisions)
3. **Capture**
   - Artifacts committed to the repo
4. **Closure**
   - Chat ends

Open-ended chats are considered a failure mode.

---

## Authority Model

ChatGPT output has **zero authority** until captured in the repo.

Authority order:
1. EXEC_SUMMARY.md
2. VERSIONING.md
3. GOVERNANCE.md
4. Release notes
5. Canonical guides
6. Implementation
7. Chat output (temporary)

If chat output conflicts with repo docs, **the repo wins**.

---

## Anti-Patterns (Explicitly Disallowed)

- “Let’s just remember this”
- Continuing unrelated work in the same chat
- Making decisions without updating docs
- Treating ChatGPT as institutional memory
- Large, multi-purpose chats

These lead directly to system decay.

---

## Escalation Rule

If during a chat you identify:
- A contract violation
- A safety weakening
- A governance conflict

You must:
1. Stop
2. Identify the affected authority document
3. Update it *before* proceeding

---

## Final Rule

> **If ChatGPT disappears tomorrow, this project must remain fully operable.**

If that statement is not true, the process has failed.

---

## Deterministic Review System

Local advisory run:
- `PYTHONPATH=. uv run python -m tools.review.run_review --mode advisory --report-path review_report.json`

Opt-in pre-push hook:
- Install: `./scripts/install-pre-push-hook.sh`
- Strict local enforcement (optional): `CODEX_REVIEW_STRICT=1 .git/hooks/pre-push`

CI behavior:
- The `review-checks` workflow runs `uv run python -m tools.review.run_review --mode strict --report-path review_report.json`.
- Exit code `2` indicates objective violations and blocks CI; exit code `1` indicates runner error.

Orchestrator evidence collection (opt-in, non-enforcing):
- Set `ORCH_COLLECT_REVIEW=1` to collect `.orchestrator_logs/<run_id>/review_report.json`
  (or `<evidence_dir>/<run_id>/review_report.json` in external mode).
- The orchestrator records `review_report_path` and `review_schema_version` in
  `.orchestrator_logs/<run_id>/manifest.json` (or `<evidence_dir>/<run_id>/manifest.json`).

Evidence index query (read-only, deterministic):
- Use `tools.evidence.cli` to list runs and artifacts from `.orchestrator_logs/evidence_index.json`.
- See `docs/evidence/EVIDENCE_INDEX.md` for command examples and schema overview.

---

## Status

This playbook is effective as of **v1.0.0**  
Changes require governance review and versioning alignment.
