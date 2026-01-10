> **Documentation Contract (v1.x)**  
> This document describes the system as it exists today.  
> It does not propose new behavior, defaults, or capabilities.
### 1. Purpose and Scope

The Skill Backlog defines **reusable patterns and conventions** for authoring Task Packs, acceptance criteria, and solution implementations within the Codex Orchestrator.

Skills:

- are documentation artifacts (not runtime features),
    
- describe _how to express work_, not _what the system can do_,
    
- are independent of orchestrator logic.
    

Skills do not grant capabilities; they encode **best-known patterns** that remain within v1 constraints.

---

### 2. Skill Taxonomy Rules

- **Pillar-first**
    
    - `security-*`, `web-*`, `game-*`
        
- **Platform-level**
    
    - `orch-*`
        
- **Solution-specific**
    
    - Treated as subsets of a pillar, not a separate axis
        
- **No implicit behavior**
    
    - Skills must not assume plugins, network, or cloud access unless explicitly declared
        

---

### 3. Orchestrator / Platform Skills (`orch-*`)

These skills describe how to work _within_ the system safely and correctly.

- `orch-taskpack-authoring`  
    Authoring self-contained, runnable Task Packs with clear scope and contracts.
    
- `orch-acceptance-patterns`  
    Writing command-based, machine-checkable acceptance criteria.
    
- `orch-validator-expectations`  
    Understanding scope, artifact, and evidence enforcement.
    
- `orch-plugin-authoring` _(optional)_  
    Writing solution plugins that remain gated, stateless, and contract-subordinate.
    
- `orch-pr-hygiene-and-release-notes`  
    Branching, commits, PR structure, and evidence attachment.
    

---

### 4. Security Engineering Skills (`security-*`)

Security skills focus on expressing **validation, analysis, and evidence** as Task Packs.

#### Core security patterns

- `security-logging-and-telemetry-basics`
    
- `security-input-validation-and-sanitization`
    
- `security-secret-hygiene-and-redaction`
    
- `security-threat-model-lite`
    
- `security-ci-security-gates`
    

#### Security solution domains (examples, not exhaustive)

- `security-bas-validation-patterns`
    
- `security-attackiq-integration-basics`
    
- `security-asm-surface-inventory-patterns`
    
- `security-ctem-exposure-tracking-patterns`
    
- `security-detection-validation-and-mapping`
    
- `security-dfir-analysis-and-evidence-packaging`
    
- `security-security-reporting-and-artifacts`
    

All security skills:

- use the same Task Pack structure,
    
- rely on the same acceptance model,
    
- assume no special platform privileges.
    

---

### 5. Web Development Skills (`web-*`)

Web skills encode common service and application patterns.

- `web-fastapi-service`
    
- `web-api-error-contracts`
    
- `web-auth-session-basics`
    
- `web-react-component-patterns`
    
- `web-nextjs-standard`
    
- `web-ci-build-and-test-patterns`
    

Web skills do not imply deployment automation or runtime hosting unless explicitly constrained.

---

### 6. Game Development Skills (`game-*`)

Game skills focus on deterministic development and content workflows.

- `game-godot-2d-loop`
    
- `game-godot-state-machines`
    
- `game-unity-csharp-patterns`
    
- `game-procgen-toolkit`
    
- `game-save-load-persistence`
    
- `game-ci-build-validation`
    

Game skills remain compatible with headless validation and artifact-based evidence.

---

### 7. Explicit Non-Goals

The Skill Backlog does **not** include skills for:

- autonomous agents
    
- memory persistence across runs
    
- background services or daemons
    
- platform-level security intelligence
    
- default-on plugins or network access
    

Any such capability would require a system-level change, not a skill.

---

### Assumptions made

- Skills are documentation and guidance, not executable features.
    
- Security breadth matters, but no single security tool defines the platform.
    
- Plugin skills must remain optional and clearly marked.
    
- The backlog should remain stable across v1.x with additive growth only.
    

---