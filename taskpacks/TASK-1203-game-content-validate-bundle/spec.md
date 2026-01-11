# TASK-1203 — Validate content + bundle evidence

## Goal
- Validate a small narrative/events JSON file for shape and referential integrity.
- Produce a deterministic content bundle (zip).
- Emit evidence artifacts for auditability.

## Content rules (minimal)
- `events.json` is a list of objects
- required fields: `id`, `title`, `choices`
- `id` must be unique
- each choice must have: `text`, `next_id` (may be null for terminal)
- any non-null `next_id` must refer to an existing event id

## Out of scope
- No engine build (no Godot/Unity invocation)
- No deployment language
- No network calls

## Acceptance
See `acceptance.yml`.

## Reviewer checklist

- [ ] Acceptance completed with no failures (`LINT_CHECK_OK`, validation OK, bundle written)
- [ ] `artifacts/validation_report.json` exists and shows:
  - [ ] `taskpack_id` = `TASK-1203-game-content-validate-bundle`
  - [ ] `status` = `ok`
  - [ ] `event_count` and `unique_ids` are non-zero
  - [ ] `broken_links` = `[]`
- [ ] `artifacts/content_bundle.zip` exists and contains:
  - [ ] `content/events.json`
  - [ ] `content/schema_notes.md`
- [ ] Content validation enforces:
  - [ ] Unique event IDs
  - [ ] Valid `next_id` references or `null`
- [ ] No engine build, binary compilation, or deployment behavior is present
