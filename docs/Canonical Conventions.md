> **Documentation Contract (v1.x)**  
> This document describes the system as it exists today.  
> It does not propose new behavior, defaults, or capabilities.
### Repo + Branching
- Default branch: `main`
- Working branches: `codex/<taskpack-id>-<slug>` (created by orchestrator)
- PR titles: `[TASK-####] <title>`
- Commit style:
    - `chore:` scaffolding/infra
    - `feat:` new capability
    - `fix:` bugfix
    - `docs:` docs only
    - `test:` tests only
### Task Packs (unit of work)
Location: `taskpacks/<TASK-ID>-<slug>/`
Required files:
- `task.yml`
- `spec.md`
- `acceptance.yml`
- `risk.md`
- `runbook.md`
Rules:
- Every task pack must be runnable in isolation.
- Acceptance criteria must be machine-checkable when possible.
- Default constraints: `allow_network: false`, `allow_cloud_mutations: false`.
### Skills
Location: `.codex/skills/<skill-name>/SKILL.md`
Naming:
- `python-*` for Python patterns
- `bas-*` for BAS patterns
- `attackiq-*` for AttackIQ-specific skills
- `web-*` for web development skills
- `game-*` for game development skills
### Orchestrator
- Runs in GitHub Actions via `workflow_dispatch`.
- Circuit breakers:
    - `max_attempts_per_phase`: 2
    - `max_total_changed_lines`: 800
    - repeated error signature limit: 2
- Always produces `.orchestrator_logs/manifest.json` + logs so artifacts are downloadable.
### Safety
- SAFE mode is default.
- Network tools prompt; secret reads forbidden.
- Any task needing internet/cloud writes must declare it in taskpack constraints.