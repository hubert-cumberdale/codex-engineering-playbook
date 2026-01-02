# Codex Orchestrator — Release Notes
## Version v1.0.0

Release Date: YYYY-MM-DD  
Status: Production-stable, contract-locked

---

## Summary
v1.0.0 marks the first **formal, stable release** of Codex Orchestrator.

This release establishes a **two-plane engineering system** with:
- Explicit work units (Task Packs)
- Bounded autonomy
- Safety-by-default execution
- Evidence-backed outcomes

From this point forward, v1 behavior is considered **contractual**.

---

## Major Features

### Control Plane / Data Plane Separation
- ChatGPT operates as the **control plane**
- Codex (CLI + GitHub + Actions) operates as the **execution plane**
- Strategy and execution are intentionally decoupled

---

### Task Packs (Atomic Unit of Work)
- All work is expressed as Task Packs
- Self-contained, reproducible, auditable
- Machine-checkable acceptance criteria enforced

---

### Safety Model (Default-On)
- SAFE mode enabled by default
- Network access disabled unless explicitly declared
- Cloud mutations disabled unless explicitly declared
- Secret access is forbidden and enforced by execpolicy

---

### Orchestrator Pipeline
- Fixed phases: Plan → Implement → Test → PR
- Circuit breakers prevent runaway execution
- Failure is first-class and auditable

---

### Evidence & Auditability
Every run produces:
- A manifest
- Phase logs
- A human-readable summary

Artifacts are uploaded even on failure.

---

## Scope of v1.0.0

### Included
- Stable orchestrator pipeline
- Task Pack schema
- Safety and execpolicy enforcement
- Circuit breakers
- Repo and workflow conventions
- AttackIQ-first BAS alignment

### Explicitly Excluded
- Long-lived agents
- Cross-task memory
- Unbounded retries
- Implicit shared state
- Vendor lock-in

---

## Breaking Changes
None (initial release).

---

## Upgrade Notes
Not applicable.

---

## Known Limitations
- Task Packs cannot compose other Task Packs
- No platform-agnostic BAS schema yet (addressed in v2)
- Operator UX is CLI/log driven

---

## Final Note
v1.0.0 is intentionally conservative.

It favors:
- Safety over speed
- Evidence over convenience
- Explicitness over autonomy

All future work must respect this foundation.
