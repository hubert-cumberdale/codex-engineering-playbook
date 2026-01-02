# codex-engineering-playbook
# Codex Engineering Playbook

This repository contains the **Codex Orchestrator** — a fault-tolerant engineering system where:

- **ChatGPT acts as the control plane**
- **Codex (CLI + GitHub + Actions) acts as the execution plane**

The system is optimized for **security engineering, web development, and game development**, with strict safety, reproducibility, and auditability guarantees.

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
- **Task Packs:** `./taskpacks`  
- **Orchestrator:** `./tools/orchestrator/orchestrate.py`
- **Plugins (v2):** `./tools/orchestrator/plugins`
- **Solutions:** `./solutions`


---

## Rule of Thumb

If a question cannot be answered by:
1. EXEC_SUMMARY.md  
2. VERSIONING.md  
3. GOVERNANCE.md  

…it is either undefined or out of scope.

---

## Quickstart

Run a taskpack locally:

```bash
TASKPACK_PATH=taskpacks/TASK-0102-orchestrator-plugin-arch \
RUN_CODEX_SMOKE=false \
python tools/orchestrator/orchestrate.py
```

Enable plugins:
```bash
BASE_BRANCH=main \
ORCH_BRANCH_NAME=codex/task-0102 \
ORCH_ENABLE_PLUGINS=1 \
TASKPACK_PATH=taskpacks/TASK-0102-orchestrator-plugin-arch \
RUN_CODEX_SMOKE=false \
python tools/orchestrator/orchestrate.py
```

Artifacts live in `.orchestrator_logs/`