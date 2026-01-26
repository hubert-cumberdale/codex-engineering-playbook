# Spec — TASK-2001 aiq-cli Results View Modes

## Goal
Implement the **Results** tab “View Mode” selector and supporting scaffolding so the
TUI can represent results/logs via three API-backed entry points:

- **Summaries** → `/v1/results`
- **Phases** → `/v1/phase_results`
- **Logs** → `/v1/phase_logs`

This is still **read-only** and must remain layout-first.

## Authoritative contracts (must read first)
- `docs/UX_MODEL.md` (authoritative UX contract)
- `docs/GOVERNANCE.md`
- `docs/CURRENT_WORK.md`

If any contract conflicts with this spec, the contract wins.

## Non-goals (explicit)
- No remote mutation (no scheduling, execution, rerun, tagging, editing)
- No auth changes beyond existing Settings workflow
- No real API networking required for this task (stubs/mocks acceptable)
- No charts/analytics

## Required UX behavior
In the Results tab:
1. Add an in-tab selector: **View: Summaries | Phases | Logs**
   - Default: **Summaries**
   - Switching modes updates the **left list pane** contents and resets selection.

2. Preserve canonical layout:
   - Split pane
   - Inline filter bar
   - Detail pane sections (placeholders acceptable)

3. Detail pane section order (must exist, placeholders ok):
   1) Metadata (always visible)
   2) Associated scenario summary
   3) Outcome
   4) Phases
   5) Logs
   6) Export (read-only)

4. “3 scenario” provider model:
   - **Summaries mode** list derives from result summaries
   - **Phases mode** list derives from phase results grouped by `result_summary_id` (fallback `scenario_job_id`)
   - **Logs mode** list derives from phase logs grouped by `result_summary_id` (fallback `scenario_job_id`)

5. Joining + fallback rule (must be explicit in UI):
   - Prefer `result_summary_id`
   - Fallback to `scenario_job_id`
   - If neither is available for a section, show:
     - `Not available (missing join key)` in that section
   - No silent empty panes.

6. Performance posture:
   - Do not load logs/phases until selected (or until mode requires it)
   - Keep UI responsive for 100s–1000s list size (test stubs ok)

7. Errors:
   - All errors appear as banners (no modal dialogs)
   - Banner text must be actionable.

## Data model guidance (no networking required)
Define internal dataclasses / dict shapes that represent the minimal fields for:
- ResultSummary
- PhaseResult
- PhaseLog
- ResultGroupKey (grouping by result_summary_id/scenario_job_id)

These may be populated via stub providers (in-memory lists) for now.

## Acceptance criteria
- `python -m pytest -q` passes.
- New/updated tests validate:
  - Results tab exists
  - View selector exists and defaults to Summaries
  - Switching modes updates list source (can be asserted via UI tree ids/classes)
  - Placeholder sections exist in correct order
  - Banner area still present and used for errors (smoke assertion)

## Deliverables
- Results tab view selector + wiring
- Provider scaffolding supporting three modes (stubbed)
- Tests updated/added accordingly
- No changes outside `scope.allowed_paths`

