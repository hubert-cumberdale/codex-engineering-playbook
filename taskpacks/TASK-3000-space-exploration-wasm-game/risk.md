# Risk Assessment (Game)

## Scope of change
- **In scope:** deterministic flight simulation, state transitions, build/export
  configuration, offline imagery ingestion, asset manifests, validation logs.
- **Out of scope:** live services, runtime downloads, manual QA acceptance.

## Primary risks
1. **Non-determinism**
   - Risk: Flight behavior varies by frame rate or device.
   - Mitigation: Fixed timestep simulation and seeded randomness.

2. **WASM export drift**
   - Risk: Engine or export template changes produce unstable outputs.
   - Mitigation: Pin engine version and record build metadata in artifacts.

3. **Asset pipeline breakage**
   - Risk: NASA imagery imports or metadata mapping become inconsistent.
   - Mitigation: Maintain an asset manifest and validate imports in headless runs.

4. **Mobile input variance**
   - Risk: Touch input mapping behaves differently across devices.
   - Mitigation: Use a single control abstraction and test via scripted input.

## Safety & reproducibility guarantees (v1)
- No network access at runtime or validation time.
- No secrets or cloud mutations.
- Deterministic headless validation signals.
- Evidence artifacts stored under stable paths.

## Rollback / recovery plan
- Revert the change set or Task Pack.
- Remove or replace imagery sets that fail validation.
- Re-run headless validation after restoring pinned engine/export versions.
