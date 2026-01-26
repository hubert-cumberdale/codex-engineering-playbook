# Release Notes — v1.1.0

## Summary
This release introduces gated support for v2 solution plugins within the Codex Orchestrator.

## Added
- Optional execution of solution plugins via `ORCH_ENABLE_PLUGINS=1` / `--enable-plugins`.
- v2 plugin runner integration with structured execution context.
- Plugin execution results recorded in `.orchestrator_logs/<run_id>/manifest.json`
  (or `<evidence_dir>/<run_id>/manifest.json` in external mode).
- Normalized, portable artifact paths in plugin results.
- Branch and PR safeguards to prevent duplicate PR creation.

## Changed
- No default behavior changes; plugin execution is opt-in only.

## Safety & Compatibility
- All v1.0.0 safety guarantees remain intact.
- Network and cloud mutations remain explicitly gated via taskpack constraints.

## Known Limitations
- Only one plugin is executed per taskpack.
- Plugin lifecycle is synchronous and single-run.

## Upgrade Notes
No action required. Existing workflows continue to operate unchanged unless plugins are explicitly enabled.
