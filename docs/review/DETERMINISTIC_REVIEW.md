# Deterministic Review Runner

This document describes the deterministic review runner (`tools.review.run_review`) and how to extend it safely.

## Deterministic Check Rules
Allowed checks are objective and auditable only:
- File or directory presence checks.
- Exact filename or path contract checks.
- Deterministic parsing of local files (no heuristics, no inference, no AI/LLM usage).
- No network access.

Disallowed:
- Semantic interpretation of content.
- Heuristic scoring.
- Any nondeterministic behavior.

## Report Schema (v1)
The JSON report is the source of truth and is deterministically serialized (sorted keys, sorted violations).

Header fields:
- `schema_version` (int): current schema version.
- `generated_at` (RFC3339 UTC timestamp).
- `tool`:
  - `name`: `tools.review.run_review`
  - `version`: repo version string or `unknown`.
- `mode`: `advisory` or `strict`.
- `summary`:
  - `checks` (int)
  - `violations` (int)
  - `status`: `pass` or `fail`
- `root`: repo root path.

Violations (each entry):
- `id` (stable rule identifier, e.g. `DOCS_TIER1_MISSING`).
- `category` (enum): `docs`, `taskpack`, `repo`, `tooling`.
- `severity` (enum): `error` (objective violations only; `warn` reserved).
- `message` (deterministic human-readable string).
- `path` (repo-relative path when applicable).
- `details` (object, optional; deterministic and JSON-serializable only).

Violation ordering is stable and sorted by `id`, then `path`, then `message`.

## Extending Checks
1) Implement a new check function in `tools/review/run_review.py` (or a new module imported there).
2) Return a list of violations using `build_violation(...)`.
3) Register the check in the `CHECKS` list.

### Selecting a Stable ID and Category
- IDs must be stable, descriptive, and uppercase snake case.
- Categories must be one of: `docs`, `taskpack`, `repo`, `tooling`.
- Do not reuse an ID for a different rule.

### Severity
- Use `error` for objective violations.
- `warn` is reserved for future use and must remain deterministic if introduced.

## Tests
Add or update tests in `tools/review/tests/test_run_review.py`:
- Positive cases (no violations).
- Negative cases (one or more violations).
- Schema header fields are present and correct.
- Violation ordering is deterministic.

Tests must remain deterministic and avoid network access.
