# Status: Detection Strategy Generator

This document tracks maturity and scope.

---

## Current Stage
**Stage 0 — Contract + Governance Locked** ✅

No production code exists yet. This stage defines the invariants that all future work must satisfy.

---

## Roadmap (high level)

### Stage 1 — STIX Extraction (MITRE-only)
- Load pinned ATT&CK STIX bundle
- Extract detection strategies + analytics
- Normalize into internal models
- Unit tests with minimal fixtures

### Stage 2 — ADS Markdown Rendering (MITRE-only)
- Jinja templates for 10-section ADS doc
- Golden file tests
- Required-section enforcement
- Provenance block enforcement

### Stage 3 — Company Profiles + Overlays
- Profile schema + deterministic merge logic
- Telemetry matrix + gap callouts
- Ownership/priority/response/validation injections

### Stage 4 — Rule Reference Enrichment (CTID first)
- Provider interface
- CTID mappings dataset ingestion (offline, pinned)
- Technique/sub-technique → rule references
- Provenance and dataset hash recording

### Stage 5 — Codex Task Pack Integration
- Task Pack templates
- Acceptance criteria (format/lint/tests/golden)
- CI wiring
- Evidence artifacts

---

## Non-goals (v1)
- Generating or translating full detection rule logic
- Heuristic technique mapping not explicitly present in sources
- Auto-remediation or SOAR execution
