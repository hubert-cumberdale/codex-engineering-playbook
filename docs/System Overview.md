> **Documentation Contract (v1.x)**  
> This document describes the system as it exists today.  
> It does not propose new behavior, defaults, or capabilities.
### 1. Purpose and Scope

The Codex Orchestrator is a **contract-driven engineering execution system** designed to safely, reproducibly, and audibly implement scoped work inside a Git repository.

It provides a structured way to:

- express work as small, self-contained units,
    
- execute that work deterministically via local commands,
    
- enforce safety and scope constraints,
    
- and produce machine-verifiable evidence for every run.
    

The system is **engineering-domain agnostic** and currently supports three primary solution domains:

- Security engineering
    
- Web development
    
- Game development
    

Security tooling (including ASM, CTEM, BAS, DFIR, SOAR) is supported as a **solution domain**, not as the system’s control plane or organizing principle.

---

### 2. Non-Negotiable v1 Guarantees

The following guarantees apply to **all runs**, regardless of solution domain or plugin usage:

- **Safety by default**
    
    - No network access unless explicitly declared
        
    - No cloud mutations unless explicitly declared
        
    - No secret reads
        
- **Reproducibility**
    
    - All work is defined in versioned files
        
    - All execution is bounded and repeatable
        
- **Auditability**
    
    - Every run produces logs and a manifest
        
    - Artifacts are treated as first-class evidence
        
    - Evidence index provides a read-only, deterministic inventory of evidence
        
- **No implicit state**
    
    - No long-lived agents
        
    - No cross-task memory
        
    - No hidden or emergent context
        

These guarantees are preserved across v1.x releases.

---

### 3. What the System Is (and Is Not)

**The system is:**

- A deterministic orchestration layer over repository-defined work
    
- Contract-driven and validator-enforced
    
- Evidence-first and CI-friendly
    

**The system is not:**

- An autonomous agent framework
    
- A background task runner
    
- A long-horizon planner with memory
    
- A vendor-locked platform
    

---

### 4. Unit of Work: Task Packs

A **Task Pack** is the atomic unit of work.

Each Task Pack:

- is self-contained
    
- is runnable in isolation
    
- declares explicit constraints
    
- defines machine-checkable acceptance
    
- produces auditable artifacts
    

If work cannot be expressed as a Task Pack, it does not belong in the system.

---

### 5. Orchestration Model

The orchestrator:

- runs in GitHub Actions or locally,
    
- executes bounded phases,
    
- applies safety constraints,
    
- invokes acceptance checks,
    
- and opens or updates pull requests with evidence.
    

There is **no implicit intelligence** in the orchestrator.  
All authority comes from repository files and declared contracts.

---

### 6. Acceptance and Validation Model

Acceptance is:

- **command-based**, not descriptive
    
- executed locally within the task scope
    
- enforced by validator scripts
    

Typical acceptance includes:

- formatting
    
- linting
    
- tests
    

Validators enforce:

- scope boundaries
    
- artifact presence
    
- evidence posture
    
- contract compliance
    

Acceptance is binary: a task either satisfies its contract or it does not.

Deterministic evidence tooling:
- `tools.review.run_review` produces a versioned review report (schema v1).
- `tools.evidence` builds a read-only evidence index (schema v1) and provides query commands.
- Orchestrator collection is opt-in via `ORCH_COLLECT_REVIEW=1` and `ORCH_WRITE_EVIDENCE_INDEX=1`.

---

### 7. Plugins (Optional, Gated)

Plugins provide **solution-specific execution paths**.

Key properties:

- Disabled by default
    
- Enabled only via explicit flags (`ORCH_ENABLE_PLUGINS`)
    
- Cannot introduce implicit state or background execution
    
- Must emit structured artifacts
    

Plugins are **not a second control plane**.  
They are an optional execution mechanism that remains subordinate to Task Pack contracts.

---

### 8. Solution Domains

The system supports multiple solution domains without changing core behavior:

- **Security engineering**
    
    - Includes BAS, DFIR, ASM, CTEM, validation, and control testing
        
- **Web development**
    
    - Services, APIs, frontends, and tooling
        
- **Game development**
    
    - Engines, loops, state systems, and content pipelines
        

Each domain:

- uses the same Task Pack structure
    
- uses the same acceptance model
    
- inherits the same safety guarantees
    

---

### 9. Operating Principle

**Truth comes from repository files, not from chat history.**

The orchestrator executes what is declared—nothing more, nothing less.

---

### Assumptions made

- v1.3.0 behavior is frozen and authoritative.
    
- Acceptance remains command-only (no remote validation).
    
- Plugins are considered stable but non-default.
    
- No domain has special privileges at the platform level.
    

---
