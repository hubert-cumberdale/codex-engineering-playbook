# Risks & mitigations

## Risk: “web” misconstrued as deployment automation
Mitigation:
- Outputs are static files only; no hosting, no deploy steps, no infra language.

## Risk: non-deterministic builds
Mitigation:
- Builder avoids timestamps and random values.
- Manifest records sha256 of inputs/outputs for traceability.

## Risk: broken links unnoticed
Mitigation:
- Link verification is part of `acceptance.must`.
