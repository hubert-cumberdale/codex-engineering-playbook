# Documentation Taxonomy

This document defines **where authoritative knowledge lives** in the Codex Orchestrator repository.

The goal is to prevent:
- Documentation sprawl
- Conflicting sources of truth
- Implicit system assumptions
- “Where does this belong?” confusion

---

## Documentation Tiers (Authority Model)

All documentation falls into one of three tiers.

### Tier 1 — Contract & System Authority
**Defines what the system is, how it behaves, and what it guarantees.**

If Tier 1 documents conflict, the more specific contract wins.

**Location:** `/docs`

Includes:
- System Overview.md
- Architecture & Roadmap.md
- Current Status.md
- Skill Backlog.md
- Canonical Conventions.md
- EXEC_SUMMARY.md
- GOVERNANCE.md
- VERSIONING.md
- CHAT_PLAYBOOK.md
- TEAM_GUIDE.md
- Release notes under `/docs/releases/`

Canonical Conventions.md governs terminology and interpretation across all Tier 1 documents.

Rules:
- Must reflect *current reality*, not aspiration
- Must preserve v1 safety, reproducibility, and audit guarantees
- Changes imply governance impact
- PR review required

---

### Tier 2 — Usage & Application
**Explains how to use the system correctly within Tier 1 constraints.**

**Locations:**
- `/taskpacks/**`
- `/solutions/**`
- `/.codex/skills/**`
- Templates and examples

Includes:
- Task Pack specs, runbooks, risks
- Solution READMEs
- Skill definitions
- Templates

Rules:
- Must not contradict Tier 1
- Must not redefine system behavior
- May reference plugins only if explicitly gated
- No aspirational or agentic language

---

### Tier 3 — Implementation
**Implements behavior but does not define it.**

**Locations:**
- `/tools/**`
- `/tests/**`
- CI / workflow files
- Code comments

Rules:
- Not authoritative
- Governed by tests and validators, not docs
- May change freely as long as contracts hold

---

## Root README (`/README.md`)

The root README is **non-authoritative**.

Purpose:
- Project entry point
- High-level orientation
- Pointers into `/docs`

Rules:
- Must not redefine architecture or guarantees
- Must defer to Tier 1 docs for truth

---

## Documentation Change Rule

> If a document can change how a new contributor understands the system,
> it is Tier 1 and belongs in `/docs`.

---

## What Does *Not* Belong in Documentation

- Debug logs
- One-off decisions
- Temporary experiments
- Long-form exploratory discussions

Those belong in:
- PRs
- Issues
- Short-lived chats

---

## Rule of Portability

Any durable knowledge must be:
- Written down
- Versioned
- Discoverable

If it can’t survive a repo clone, it doesn’t belong.
