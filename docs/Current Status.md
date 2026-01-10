> **Documentation Contract (v1.x)**  
> This document describes the system as it exists today.  
> It does not propose new behavior, defaults, or capabilities.

> **Status as of:** v1.1.0 (v1.2.0 scaffolding in progress)
### 1. Current State (Post v1.1.0)

As of **v1.1.0**, the Codex Orchestrator is **stable, contract-driven, and production-safe** for its intended scope.

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

### 6. Near-Term Direction (v1.x, High-Level)

Planned work remains **documentation- and coverage-focused**, not architectural:

1. **Documentation alignment**
    - Ensure all resource docs reflect current, not aspirational, behavior
2. **Solution coverage expansion**
    - Starter layouts and exemplars for:
        - security (beyond BAS)
        - web
        - game
3. **Task Pack templates**
    - Pillar-specific examples
    - Acceptance patterns tuned per domain
    - No orchestrator changes
4. **Skill catalog alignment**
    - Pillar-first taxonomy
    - Security solutions treated as domains, not the platform center

All planned work is **contract-safe** and preserves v1 guarantees.
### Next (v1.x, contract-safe)

1) v1.2.0 scaffolding and coverage (in progress)
   - Solution directory structure created for security, web, and game
   - Web Task Pack template walkthrough added
   - Security Task Pack template walkthrough added
   - Game Task Pack template walkthrough added
   - Skill docs added to support web acceptance and build evidence patterns

2) Example Task Packs (next)
   - Create small, realistic example Task Packs per pillar
   - Use templates and walkthroughs without changing orchestrator behavior
   - Ensure examples are validator-clean and evidence-first

3) Continued documentation hygiene
   - Keep Tier 1 docs aligned with current reality
   - No aspirational or roadmap-driven language

---

### Assumptions made
- v1.1.0 is the baseline and will not be re-interpreted.
- “Current Status” must describe _operational truth_, not intent.
- Security breadth is important, but the platform remains solution-agnostic.
- No roadmap item implies default-on behavior.

---