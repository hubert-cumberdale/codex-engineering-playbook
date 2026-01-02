# Documentation Taxonomy

This document defines **where knowledge lives** in the Codex Engineering Playbook.

The goal is to prevent:
- Documentation sprawl
- Duplicate authority
- Tribal knowledge
- “Where should this go?” confusion

---

## Authority Levels (Highest → Lowest)

1. EXEC_SUMMARY.md  
2. VERSIONING.md  
3. GOVERNANCE.md  
4. Release Notes  
5. Canonical Conventions  
6. Implementation Details  

If documents conflict, **higher authority wins**.

---

## Documentation Zones

### 🟥 Root (Contract & Authority)
Location: `/`

Contains:
- EXEC_SUMMARY.md
- VERSIONING.md
- GOVERNANCE.md
- README.md (pointer only)

Rules:
- Low frequency of change
- Changes imply governance impact
- PR review required

---

### 🟧 `/docs/releases/` (Historical Record)
Contains:
- Immutable release notes
- Versioned change summaries

Rules:
- Never edit past releases
- Append only
- No design discussion

---

### 🟨 Canonical Guides
Locations:
- `AGENTS.md`
- `TEAM_GUIDE.md`
- `Canonical Conventions.md`

Contains:
- How the system is used
- How contributors should behave
- Stable operational guidance

Rules:
- Updated deliberately
- Must align with v1 contracts

---

### 🟩 `/taskpacks/` (Executable Knowledge)
Contains:
- Work units
- Specifications
- Acceptance criteria
- Risk models

Rules:
- Self-contained
- Runnable in isolation
- No hidden dependencies

---

### 🟦 `/.codex/skills/` (Reusable Capability)
Contains:
- Skills
- Patterns
- Execution primitives

Rules:
- Reusable across task packs
- No scope decisions
- No policy overrides

---

### 🟪 Implementation Docs
Locations:
- Inline code docs
- Tool-specific READMEs

Rules:
- Lowest authority
- Must not redefine system behavior

---

## What Does *Not* Belong in Docs

- Debug logs
- One-off decisions
- Temporary experiments
- Long-form discussions

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
