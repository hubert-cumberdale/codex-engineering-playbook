# Game Development Task Pack Template

This template is used for **game development tasks** focused on code, structure, or assets that can be validated deterministically.

---

## When to use this

Use this template for tasks such as:
- Project or scene scaffolding
- Game loop or state machine implementation
- Save/load or persistence systems
- Engine tooling or editor scripts
- Deterministic gameplay logic

This template supports:
- Engine-specific work (e.g., Godot, Unity)
- Engine-agnostic logic and tooling

Real-time playtesting and subjective evaluation are out of scope.

---

## What this template assumes

- **Deterministic validation**
  - Headless builds, scripted checks, or static validation
- **Engine version pinned**
  - Toolchain and engine versions must be explicit
- **Structure over polish**
  - Focus on correctness, architecture, and repeatability
- **Evidence over experience**
  - Logs, build output, or test results determine success

Graphics quality, tuning, and “feel” are intentionally excluded.

---

## How to instantiate

1. Copy this directory to a new task pack:
```bash
   cp -r taskpacks/_templates/game taskpacks/<TASK-ID>-<slug>
```
2. Update:
- `task.yml`: engine, version, and constraints
- `spec.md`: gameplay or system objective
- `acceptance.yml`: build, script, or logic checks
- `risk.md`: engine compatibility or regression risks
- `runbook.md`: how to validate deterministically
3. Verify:
- The task pack does not rely on manual playtesting
- Acceptance criteria are objective
- Outputs can be reviewed without running the game interactively

If success depends on subjective gameplay feel, it belongs outside this system.