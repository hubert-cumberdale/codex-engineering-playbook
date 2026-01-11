# v1.2 Pressure Checklist (Tier-2)

> Status: Informational / Planning  
> Scope: Docs, templates, and hygiene Task Packs  
> Does not introduce system behavior, validators, or enforcement

This checklist tracks **known friction points** discovered during v1.x usage
and defines what “done” means for v1.2 hygiene.

---

## P0 — Contributor footguns

### P0.1 Python import path rules in Task Packs
**Pressure**
- Scripts under `tools/` importing `src.*` often fail with `ModuleNotFoundError`.

**Pattern**
- Add repository root to `sys.path` inside scripts under `tools/`.

**Done when**
- Templates and walkthroughs document the pattern.
- Hygiene checks can flag missing path bootstraps (heuristic).

---

### P0.2 Unittest discovery inconsistency
**Pressure**
- `python -m unittest -q` frequently results in “Ran 0 tests”.

**Pattern**
```bash
python -m unittest discover -s tests -p "test_*.py" -q
```

---

**Done when**
- Templates standardize on explicit discovery.
- Hygiene checks warn on non-discovery usage.

### P0.3 Deterministic evidence artifacts
**Pressure**
- Timestamps, unstable ordering, and environment-specific fields cause review friction.

**Rules**
- No timestamps (`generated_at`, `created_at`, etc.)
- Stable ordering
- Hash inputs/outputs
- Fixed zip metadata when bundling

**Done when**
- Rules documented
- Hygiene checks flag common timestamp keys

---

## P1 — Review ergonomics
### P1.1 Evidence envelope consistency

**Pressure**
- Each Task Pack invents a new artifact schema.

**Recommended envelope**
```json
{
  "taskpack_id": "...",
  "inputs": {...},
  "outputs": {...},
  "status": "ok|failed",
  "errors": []
}
```

---

**Done when**
- Guidance exists (non-enforcing)
- Examples follow the pattern

### P1.2 Expected output snapshots
**Pressure**
- Reviewers must re-run commands to understand artifacts.

**Pattern**
- `runbook.md` includes:
    - example console output
    - example artifact excerpts (shape only)

**Done when**
- Templates include snapshot sections

---

## P2 — Layout & lifecycle clarity
### P2.1 Task Pack I/O conventions

**Pattern**
- `data/` — inputs
- `src/` — logic
- `tools/` — acceptance scripts
- `artifacts/` — outputs only

**Done when**
- Documented and reflected in templates

---

### P2.2 Multi-artifact manifest (recommended)

**Pressure**
- Task Packs producing many artifacts lack a single index.

**Pattern**
`artifacts/manifest.json`:
```json
{
  "taskpack_id": "...",
  "artifacts": [
    { "path": "artifacts/report.json", "sha256": "…" },
    { "path": "artifacts/report.md", "sha256": "…" }
  ],
  "status": "ok"
}
```

**Notes**
- Information only
- Hygiene scans may recommend this pattern

**Done when**
- Guidance exists; hygiene can recommend it

---

## P3 — Governance hygiene
### P3.1 Branch naming conventions
**Pattern**
- docs/... — docs-only
- add/... or taskpacks/... — Task Packs
- Avoid parallel namespaces for same work

---

### P3.2 Task Pack PR hygiene
**Pattern**
- PRs state:
    - acceptance commands run
    - artifacts produced
    - no deploy/network behavior

---

## Notes
- This checklist is planning and guidance only
- Items graduate to “done” via docs/templates/hygiene Task Packs

---