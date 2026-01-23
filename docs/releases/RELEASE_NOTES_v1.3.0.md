# Release Notes — v1.3.0

## Summary
This release introduces a deterministic, read-only Evidence Index capability
that allows Codex to discover, index, and query execution artifacts in a
fully offline, auditable manner. The capability is opt-in and does not change
any default enforcement or orchestrator behavior.

## What’s New

### Evidence Index (new platform capability)
- Added a deterministic evidence index builder under `tools/evidence`
  that scans explicit roots (default: `.orchestrator_logs/`) and emits a
  versioned `evidence_index.json` with stable ordering.
- Introduced a read-only query CLI:
  - `list-runs`
  - `list-artifacts`
  - `show-artifact`
- Index schema is versioned (`schema_version: 1`) and contract-locked by tests.

### Orchestrator integration (opt-in, non-enforcing)
- Added optional evidence index generation after orchestrator runs.
- Enabled via environment variable:
  - `ORCH_WRITE_EVIDENCE_INDEX=1`
- When enabled:
  - Writes `.orchestrator_logs/evidence_index.json`
  - Records `evidence_index_path` and `evidence_index_schema_version`
    in the orchestrator manifest.
- Index generation is best-effort and never fails a run.

### Review system update (scoped)
- Allowlisted `tools/orchestrator/orchestrate.py` in the deterministic
  review allowlist.
- Change is fully scoped, tested, and does not alter other review behavior.

## Documentation
- Added Tier-2 documentation:
  - `docs/evidence/EVIDENCE_INDEX.md`
- Updated operator playbook pointers for evidence workflows.
- Tier-1 governance remains unchanged in scope and enforcement posture.

## Enforcement & Compatibility
- No breaking changes.
- No defaults changed.
- No new enforcement paths introduced.
- All functionality is deterministic, offline, and auditable.

## How to Use (Examples)

Generate an evidence index:
```bash
PYTHONPATH=. python -m tools.evidence.cli index \
  --root .orchestrator_logs \
  --out .orchestrator_logs/evidence_index.json
```

Query Evindence:
```bash
PYTHONPATH=. python -m tools.evidence.cli list-runs \
  --index .orchestrator_logs/evidence_index.json
```

Enable orchestrator index writing (opt-in):
```bash
ORCH_WRITE_EVIDENCE_INDEX=1 \
python tools/orchestrator/orchestrate.py
```

---