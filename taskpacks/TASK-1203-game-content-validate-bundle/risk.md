# Risks & mitigations

## Risk: content drift without detection
Mitigation:
- Validation runs in acceptance and produces a report artifact.

## Risk: non-deterministic bundles
Mitigation:
- Bundle creation uses stable file ordering and fixed timestamps in zip entries.

## Risk: confusion with “game build”
Mitigation:
- This is a content pipeline only; no engine compilation or executable build steps.
