# Tier 1 Documentation Checklist (v1.x)

This checklist applies to all **Tier 1 documents** under `/docs`.

Tier 1 documents define system behavior, guarantees, and constraints.
They are authoritative and contract-bearing.

---

## Scope & Authority
- [ ] Document lives under `/docs`
- [ ] Document explicitly describes **current reality**, not future intent
- [ ] Document does **not** redefine orchestrator behavior
- [ ] Document defers to Canonical Conventions for terminology

---

## Core Invariants
- [ ] Task Packs are the **only unit of work**
- [ ] Acceptance is **command-based and local**
- [ ] Safety is **default-on**
- [ ] Evidence and artifacts are **first-class**
- [ ] No implicit state
- [ ] No long-lived agents
- [ ] No cross-task memory

---

## Plugins
- [ ] Plugins are framed as **optional**
- [ ] Plugins are framed as **gated**
- [ ] Plugins are not described as a new control plane
- [ ] No default behavior changes implied

---

## Language Hygiene
- [ ] No aspirational language (“will”, “future”, “eventually”)
- [ ] No agentic language (“learns”, “decides”, “autonomous”)
- [ ] No implied intelligence beyond orchestration
- [ ] No implied network or cloud access

---

## Pillar Neutrality
- [ ] Security, web, and game are treated as **peer solution domains**
- [ ] Security tooling (BAS, ASM, CTEM, DFIR) is not platform-defining
- [ ] No pillar is given special privileges

---

## Final Check
- [ ] A new contributor could read this document and form a **correct mental model**
- [ ] No contradiction with other Tier 1 docs

---

> If any item fails, the document must be revised before merge.
