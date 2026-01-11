# Risks & mitigations

## Risk: evidence not reviewable / unclear
Mitigation:
- Produce both machine-readable (`report.json`) and human-readable (`report.md`) artifacts.
- Produce `schema_validation.json` with explicit status and errors.

## Risk: non-deterministic reports
Mitigation:
- Stable ordering (sorted by technique_id, then control_id).
- No timestamps or environment-dependent fields in artifacts.

## Risk: schema validation drift
Mitigation:
- Validation logic is explicit and tested.
- Validation output is itself an evidence artifact.
