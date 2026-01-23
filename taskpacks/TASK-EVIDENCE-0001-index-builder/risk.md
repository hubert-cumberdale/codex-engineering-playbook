# Risk Assessment

## Summary
Low risk. Adds read-only tooling and tests without changing orchestrator behavior.

## Risks
- Incorrect path handling could produce non-repo-relative entries.
- Non-deterministic ordering could reduce auditability.

## Mitigations
- Enforce repo-relative paths and stable sorting in the indexer.
- Tests assert ordering, schema extraction, and ignore behavior.
