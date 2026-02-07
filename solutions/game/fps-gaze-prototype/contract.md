# Task Pack Contract — FPS Gaze Prototype (Unreal 4.27)

## Purpose
Define a staged, deterministic Task Pack to bootstrap a greenfield Unreal Engine FPS prototype with optional Tobii eye tracking. The Task Pack enables independent agent work across design, engine integration, gameplay mechanics, and validation from project creation through a playable vertical slice.

## Scope
- Unreal Engine 4.27 project bootstrap for Windows PC.
- C++ + Blueprint hybrid architecture.
- Optional Tobii eye tracking input, with graceful degradation when unavailable.
- Four gaze-aware FPS mechanics:
  - Gaze-assisted aim (soft assist blended with mouse).
  - Gaze-to-interact (highlight + confirm input).
  - Clean UI (HUD visibility based on gaze zones).
  - Extended view (micro camera bias from gaze).
- Deterministic, auditable evidence for each stage.

## Non-Goals
- No raw gaze logging or research data collection.
- No cloud services, telemetry, or network dependencies.
- No gameplay logic that directly depends on Tobii SDK calls.
- No engine or gameplay implementation in this Task Pack.

## Stage Model (Contractual)
All work is staged. Each stage has explicit boundaries, required artifacts, and acceptance criteria recorded in `acceptance.yml` and `spec.md`.

### Stage 0 — Repository & Engine Bootstrap
- Unreal project creation and repo layout.
- Build and run verification.
- Evidence: engine version, project identifier, build output.

### Stage 1 — Eye Tracking Provider Abstraction
- Tobii provider component.
- Signal normalization and confidence gating.
- Null provider fallback (no Tobii).
- Evidence: signal contract and runtime validation output.

### Stage 2 — Gameplay Intent Layer
- Intent resolution for aim target, interaction target, and UI focus.
- No gameplay effects.
- Evidence: intent resolution tests or debug overlays.

### Stage 3 — Gameplay Adapters
- Aim assist adapter.
- Interaction adapter.
- UI adapter.
- Camera adapter.
- Evidence: before/after behavior captures with deterministic settings.

### Stage 4 — Vertical Slice Assembly
- Minimal arena map.
- Targets and interactables.
- HUD widgets.
- Evidence: playable slice checklist and validation outputs.

## Architectural Constraints
- Eye tracking is optional at runtime.
- All gaze signals pass through a filter and intent layer.
- Gameplay systems read only intent outputs, never raw SDK calls.
- A null provider is mandatory and active when eye tracking is unavailable.
- Gaze data retention is disallowed; no raw gaze logging.

## Determinism & Evidence
- Each stage defines explicit pass/fail criteria in `acceptance.yml`.
- Evidence artifacts use stable paths under this Task Pack.
- Validation uses command-based, local checks; no manual judgment.

## Safety and Ethics
- Player comfort and accessibility are first-class constraints.
- Camera motion from gaze uses bounded micro-bias with opt-out.
- HUD visibility changes must preserve critical information access.

## Repo Bootstrap Guarantees
- A new agent can clone the repo, follow the runbook, and reproduce all stage evidence without oral context.
- All required prerequisites and toggles are documented in `runbook.md`.

## Repository Root Invariant
- The Unreal project MUST exist under a stable, committed root path:
  - `Game/fps-gaze-prototype/` or
  - `Unreal/fps-gaze-prototype/`
- This root path is contractual and MUST NOT change across stages.
- Any change to the root path requires updating acceptance criteria and this contract.
