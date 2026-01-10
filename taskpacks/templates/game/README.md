# Game Task Pack Template — Walkthrough

This document explains how to use the **game Task Pack template** to create
a contract-safe, CI-verifiable game development change using the Codex Orchestrator.

This is a **walkthrough**, not a system definition.
Authoritative system behavior and guarantees are defined under `/docs`.

---

## What this template is for

Use the game Task Pack template when you need to:

- validate game logic, systems, or data deterministically,
- prove that a game project builds or runs in a headless mode,
- test core loops, state machines, or simulation steps,
- produce evidence artifacts that demonstrate correctness.

This template is designed for **development-time validation**, not live gameplay.

---

## What this template is NOT for

This template does **not** support:
- interactive or manual gameplay testing,
- real-time performance benchmarking,
- graphics or audio fidelity validation,
- engine editor usage in CI,
- deployment or distribution of game builds.

All game Task Packs must remain:
- headless,
- deterministic,
- and runnable in isolation.

---

## Template structure

A game Task Pack follows the standard structure:

```

taskpacks/<TASK-ID>-<slug>/
├── task.yml
├── spec.md
├── acceptance.yml
├── risk.md
├── runbook.md
└── artifacts/
└── README.md

```

Each file has a defined role and must remain self-contained.

---

## task.yml — Declaring intent and constraints

`task.yml` defines:
- the identity of the Task Pack,
- the class of game work being validated,
- execution constraints.

Game Task Packs should be explicit about:
- headless execution requirements,
- engine or runtime versions,
- whether builds or simulations are being validated.

If rendering or user input is required, the Task Pack is **out of scope**.

---

## spec.md — Defining the game contract

`spec.md` answers:
- *What system or mechanic is being validated?*
- *What deterministic behavior is expected?*
- *What constitutes success or failure?*
- *What is intentionally excluded?*

Valid game contracts include:
- “State machine transitions occur as expected.”
- “A turn-based loop completes N turns deterministically.”
- “The project builds successfully in headless mode.”

Avoid:
- subjective language (“fun”, “smooth”, “balanced”),
- player-experience claims,
- performance claims unless explicitly measured.

---

## acceptance.yml — Headless, command-based validation

Game acceptance is **command-based and headless**.

Typical patterns include:
- unit or simulation tests,
- scripted engine runs in headless mode,
- build-only validation steps.

Example pattern (conceptual):

```yaml
version: 1
must:
  - name: test
    cmd: python -m pytest -q
  - name: simulate
    cmd: ./run_headless_sim.sh
```

Rules:

* Commands must not require a display or user input.
* Execution must be deterministic across runs.
* Time-based or random behavior must be controlled or seeded.

See also:

* **Skill: game-godot-state-machines**
* **Skill: game-godot-2d-loop** (or equivalent engine skills)

---

## artifacts/ — Evidence-first game output

Artifacts are **primary proof** that the game contract holds.

Common evidence artifacts:

* simulation logs (summarized),
* turn-by-turn state outputs,
* build summaries,
* validation result files.

Example layout:

```
artifacts/
├── README.md
└── validation-contract.txt
```

### artifacts/README.md

Explain:

* what mechanic or contract was validated,
* what evidence files exist,
* what aspects of gameplay are not covered.

### Evidence files

Evidence should be:

* textual and small,
* stable across runs,
* reviewable in PRs.

Avoid:

* large binaries,
* screenshots or videos,
* engine editor output.

---

## risk.md — Declaring limitations and assumptions

`risk.md` documents:

* assumptions about determinism,
* excluded gameplay scenarios,
* engine-specific limitations.

Examples:

* “Physics behavior validated with fixed timestep only.”
* “No validation of rendering or audio subsystems.”
* “Randomness is seeded and limited to test scenarios.”

This is scoped disclosure, not a design critique.

---

## runbook.md — Human execution notes

`runbook.md` provides:

* prerequisites (engine version, CLI tools),
* how to run the Task Pack locally,
* common failure modes and troubleshooting steps.

The runbook must not:

* redefine acceptance,
* introduce interactive steps,
* bypass constraints.

---

## How this fits together

The game template combines:

* explicit, deterministic game contracts,
* headless acceptance execution,
* evidence-first artifacts,
* declared risks and assumptions,

while preserving:

* safety-by-default execution,
* CI compatibility,
* parity with web and security Task Packs.

Game Task Packs are **first-class peers**, not special cases.

---

## See also

* **Skill: game-godot-state-machines**
* **Skill: game-godot-2d-loop**
* **TASK-0102-game-headless-contract-check** — canonical game canary

---
