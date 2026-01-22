# Status: Detection Strategy Generator

This document tracks maturity and scope.

---

## Current Stage
**Stage 4 — Rule Reference Enrichment (CTID first)** 🚧

Stages 0–3 are complete (contract/governance, STIX extraction, deterministic ADS rendering, company profiles + overlays).

---

## Roadmap (high level)

### Stage 1 — STIX Extraction (MITRE-only)
- Load pinned ATT&CK STIX bundle
- Extract detection strategies + analytics
- Normalize into internal models
- Unit tests with minimal fixtures

### Stage 2 — ADS Markdown Rendering (MITRE-only)
- Deterministic 10-section ADS doc renderer
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

**Stage 4 plan (next)**
- Define provider interface and offline dataset contract
- Add deterministic loader for pinned CTID mappings
- Render rule references attached to techniques/sub-techniques (references-only; no inference)
- Record rule-reference dataset hash + provenance in a dedicated, non-semantic subsection (no impact on section count)
- Add tests for enrichment + provenance determinism

### Stage 4 — Scope & Contracts (References-Only)

#### A) In-scope MITRE object allowlist (explicit)

| Object Type | In Scope? | Allowed Attachment? | Notes |
| ----------- | --------- | ------------------- | ----- |
| `x-mitre-detection-strategy` | No | No | First-class object, but Stage 4 attachments are technique-only. |
| `x-mitre-analytic` | No | No | First-class object, but Stage 4 attachments are technique-only. |
| `attack-pattern` (technique/sub-technique) | Yes | Yes | Sole attachment point for Rule References in Stage 4 (CTID-first). |
| `x-mitre-data-source` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `x-mitre-data-component` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `course-of-action` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `intrusion-set` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `malware` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `tool` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `campaign` | No | No | Not a Rule Reference attachment point in Stage 4. |
| `relationship` | No | No | No attachments to relationship objects. |

#### B) Attachment rules (normative)
- Rule references MAY attach to `attack-pattern` objects only (technique or sub-technique).
- Rule references MUST NOT attach to detection strategies or analytics.
- Rule references MUST NOT attach to any non-`attack-pattern` MITRE object type.
- Rule references MUST NOT propagate across relationships.
- Strategy scope MUST NOT include analytic-derived aggregates.

#### C) Dataset contract (offline/pinned)
- Required fields per mapping row: `provider`, `rule_id`, and one of `technique_id` or `subtechnique_id`.
- Optional fields per mapping row: `url`, `display_name`.
- If `subtechnique_id` is present, it MUST be a full ATT&CK sub-technique ID (e.g., `T1059.003`), and no inference to parent technique is allowed.
- Dataset pinning MUST include a version identifier and a cryptographic hash recorded as provenance.
- Deterministic load requirements: no sorting unless a source order is explicitly defined; dedupe MUST be stable and first-seen only.

#### D) Rendering constraints (Stage 3 contract protection)
- No changes to existing section count or order.
- Rendering is additive only within an existing "Additional Resources" section scoped to the owning object (e.g., technique or analytic) and MUST NOT introduce new top-level sections.
- Rule references MUST be labeled with the source text: "Source: Offline CTID mapping dataset" (or equivalent).
- No coverage summaries, counts, or rollups.

#### E) Non-goals (explicit)
- No inference / ranking / scoring.
- No vendor rule logic ingestion.
- No network lookups.
- No automatic unioning of platforms/telemetry.
- No claims of detection efficacy.

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
