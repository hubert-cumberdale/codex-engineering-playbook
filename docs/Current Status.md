> **Documentation Contract (v1.x)**  
> This document describes the system as it exists today.  
> It does not propose new behavior, defaults, or capabilities.

> **Status as of:** v1.3.0
### 1. Current State (Post v1.3.0)

As of **v1.3.0**, the Codex Orchestrator is **stable, contract-driven, and production-safe** for its intended scope.

The system reliably:
- Executes Task Packs end-to-end
- Enforces safety and scope constraints
- Produces auditable evidence
- Operates consistently in local and CI environments

Completed:
- Documentation contract formalized (Tier 1 / Tier 2 / Tier 3) ✅
- Canonical Conventions established as authoritative terminology source ✅
- Tier 1 documentation checklist added and enforced for doc PRs ✅

No architectural instability is present.

---

### 2. What Is Explicitly Stable

The following are **established and relied upon**:

- **Task Packs as the unit of work**
	- Required metadata (`task.yml`)    
    - Explicit constraints
    - Machine-checkable acceptance    
- **Acceptance model**
    - Command-based (format / lint / tests)
    - Executed locally
    - Validator-enforced
    - Evidence-first
- **Safety posture**
    - SAFE mode default
    - No implicit network
    - No implicit cloud mutations
    - No secret access
- **Orchestrator execution**
    - Runs locally and in GitHub Actions
    - Bounded retries and circuit breakers
    - Deterministic phase execution
    - Always emits logs and a manifest
- **Deterministic review system**
    - Local advisory runner (`tools.review.run_review`)
    - CI enforcement of objective violations only
    - Versioned schema (v1)
- **Evidence index**
    - Read-only, deterministic index of `.orchestrator_logs`
    - Schema v1 at `.orchestrator_logs/evidence_index.json`
- **PR hygiene**
    - Stable branch naming
    - PR-exists guard (no spam)
    - Evidence attached to every change

---

### 3. What Exists but Is Gated

The following capabilities exist but are **explicitly non-default**:

- **Plugin execution**
    - Implemented and wired
	- Disabled unless `ORCH_ENABLE_PLUGINS` is set
	- Remains subordinate to Task Pack contracts
    - Cannot introduce implicit state or background behavior 
- **Orchestrator evidence collection**
    - Review report collection enabled only with `ORCH_COLLECT_REVIEW=1`
    - Evidence index writing enabled only with `ORCH_WRITE_EVIDENCE_INDEX=1`
    - Non-enforcing and best-effort
- **Solution-specific execution paths**
    - Located under `solutions/`
    - Treated as optional implementations, not platform features
    - Must obey v1 safety and audit guarantees

Plugins are a **thin extension mechanism**, not a shift in control plane.

---

### 4. Security Scope Clarification

Security is treated as a **broad solution domain**, not a single tool or methodology.

Supported security use cases include (but are not limited to):

- Breach & Attack Simulation (BAS)
- AttackIQ-based validation
- Attack Surface Management (ASM)
- Continuous Threat Exposure Management (CTEM)
- Detection engineering and validation
- DFIR workflows and analysis
- Reporting and evidence generation

All of these:
- Are expressed as Task Packs
- Use the same acceptance and safety model
- Have no special privileges in the system

---

### 5. What Is Intentionally Out of Scope (v1.x)

The following are **explicit non-goals**:
- Long-lived agents
- Cross-task memory
- Background or daemonized execution
- Autonomous decision-making outside declared contracts
- Implicit state carried between runs

Any future work must preserve these exclusions unless a major version boundary is crossed.

---

### 6. Ongoing v1.x Maintenance

Ongoing work remains **documentation- and coverage-focused**, not architectural.
It preserves v1 guarantees and avoids default behavior changes.

---

### Assumptions made
- v1.3.0 is the baseline and will not be re-interpreted.
- “Current Status” must describe _operational truth_, not intent.
- Security breadth is important, but the platform remains solution-agnostic.
- No roadmap item implies default-on behavior.

---
