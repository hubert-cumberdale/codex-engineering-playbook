# codex-engineering-playbook
# Codex Engineering Playbook

This repository contains the **Codex Orchestrator** — a fault-tolerant engineering system where:

- **ChatGPT acts as the control plane**
- **Codex (CLI + GitHub + Actions) acts as the execution plane**

The system is optimized for **security engineering and Breach & Attack Simulation (AttackIQ-first)**, with strict safety, reproducibility, and auditability guarantees.

---

## Start Here

👉 **[EXEC_SUMMARY.md](./EXEC_SUMMARY.md)**  
This is the authoritative overview of what this system is, why it exists, and what guarantees it provides.

---

## Governance & Contracts

- **[VERSIONING.md](./VERSIONING.md)** — How change is governed  
- **[GOVERNANCE.md](./GOVERNANCE.md)** — Decision authority and escalation  
- **Release history:** [`/docs/releases`](./docs/releases)

---

## Operational Docs

- **AGENTS.md** — Agent operating rules  
- **TEAM_GUIDE.md** — Human developer workflows  
- **Task Packs:** `/taskpacks`  
- **Skills:** `/.codex/skills`

---

## Rule of Thumb

If a question cannot be answered by:
1. EXEC_SUMMARY.md  
2. VERSIONING.md  
3. GOVERNANCE.md  

…it is either undefined or out of scope.
