# Spec: Deterministic Review Schema, Extensibility, and Evidence

## Objective
Harden the deterministic review report schema, document a stable extensibility contract, and add opt-in evidence collection to the orchestrator without changing default behavior.

## Requirements
### A) Schema hardening
- Add a stable schema header to `tools.review.run_review` JSON output:
  - `schema_version`: integer (start at 1).
  - `generated_at`: RFC3339 UTC timestamp.
  - `tool`: `{ "name": "tools.review.run_review", "version": "<repo version or 'unknown'>" }`.
  - `mode`: `advisory` or `strict`.
  - `summary`: `{ "violations": int, "checks": int, "status": "pass"|"fail" }`.
- Each violation entry must include:
  - `id`, `category`, `severity`, `message`, `path`, `details` (optional object).
- Define a stable category enum in code and docs: `docs`, `taskpack`, `repo`, `tooling`.
- Deterministic JSON serialization:
  - Stable key ordering.
  - Stable ordering of violations (sort by `id`, then `path`, then `message`).

### B) Extensibility documentation
- Add a developer doc describing deterministic checks, how to add/register a new check, how to choose `id`/`category`, and how to test.
- Tier-1 `GOVERNANCE.md` should only include a short pointer to the Tier-2 doc and the schema version statement.

### C) Evidence collection integration (opt-in)
- Add opt-in collection in the orchestrator using `ORCH_COLLECT_REVIEW=1`.
- When enabled, run the review runner in advisory mode and store `review_report.json` under `.orchestrator_logs/`.
- Update the manifest to include `review_report_path` and `review_schema_version` when collected.
- No behavior changes by default; collection is non-enforcing.

## Constraints
- No network access.
- No AI/LLM usage.
- No heuristics or semantic inference.
- Deterministic and auditable behavior only.
- No new dependencies.
