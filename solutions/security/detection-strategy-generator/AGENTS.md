# Agents: Detection Strategy Generator (ADS-style)

This system generates **Palantir ADS-style Detection Strategy** Markdown documents from **MITRE ATT&CK Detection Strategy + Analytic STIX objects**, optionally enriched with **references-only** detection rule mappings.

This file defines agent roles, responsibilities, and hard boundaries.

---

## Mission
Produce deterministic, auditable, source-grounded detection strategy documents that support:
- **ASM** (Attack Surface Management) coverage/telemetry alignment
- **CTEM** (Continuous Threat Exposure Management) detection posture evidence
- **BAS** (Breach & Attack Simulation) validation scaffolding

---

## Authority boundaries (non-negotiable)
- **MITRE ATT&CK STIX** is authoritative for:
  - strategy intent, scope, analytics linkages, platforms, log source references, mutable elements
- **Company profile / overlays** are authoritative for:
  - environment truth (telemetry availability), owners, priority policy, response routing, validation procedures
- **Rule providers** are authoritative for:
  - existence of mapped rules (references + metadata only), provenance, timestamps

The system MUST NOT invent detection logic, telemetry, or response steps.

---

## Agent roster

### 1) Planner (Contract Owner)
**Responsibilities**
- Define the stable document contract and invariants.
- Specify acceptance criteria for “done.”
- Define governance rules and versioning policy.

**Must not**
- Add features without updating contract docs.
- Relax provenance or determinism requirements.

**Outputs**
- DETECTION_STRATEGY_CONTRACT.md
- SOURCE_OF_TRUTH.md
- GOVERNANCE.md
- STATUS.md

---

### 2) Data Extractor (STIX Interpreter)
**Responsibilities**
- Parse ATT&CK STIX bundles and build an internal normalized model:
  - Detection Strategy objects
  - Analytic objects
  - Relationships to techniques/sub-techniques where available
  - Platform/log-source/mutable-element metadata
- Preserve provenance (IDs, versions, bundle metadata).

**Must not**
- “Fill in” missing fields by inference.
- Reword MITRE meaning beyond minimal formatting.

**Outputs**
- Normalized JSON manifest(s) for downstream rendering (internal artifact)
- Extractor unit test fixtures

---

### 3) Profile Integrator (Org Context Merger)
**Responsibilities**
- Load and validate company profile (schema-validated).
- Merge overlays deterministically.
- Provide telemetry-gap signals and local ownership/routing info.

**Must not**
- Override or reinterpret MITRE strategy intent.
- Use profile data to “rewrite” MITRE text (except inserting local placeholders).

**Outputs**
- Merged configuration object
- Telemetry gap report (artifact)

---

### 4) Renderer (ADS Markdown Author)
**Responsibilities**
- Render ADS-style Markdown using templates.
- Enforce the 10 required sections and required metadata blocks.
- Ensure “unknown” is explicit and visible.

**Must not**
- Add claims not present in authoritative inputs.
- Hide missing data.

**Outputs**
- `docs/detection-strategies/*.md`
- Index/manifest file (optional later)

---

### 5) Enricher (Rule References)
**Responsibilities**
- Attach references-only rule metadata by technique/sub-technique:
  - CTID mappings datasets (offline, pinned)
  - Platform-native sources later (API)
- Ensure provenance and reproducibility.

**Must not**
- Embed full rule bodies by default.
- Claim coverage effectiveness based solely on mapping presence.

**Outputs**
- “Rule References” appendices / subsections in docs
- Rule reference manifest (artifact)

---

### 6) Verifier (Contract + Determinism)
**Responsibilities**
- Validate that every doc meets contract requirements:
  - 10 ADS sections present
  - provenance block present
  - deterministic generation evidence
- Run golden tests and schema validation.

**Must not**
- Approve docs missing provenance or with invented fields.

**Outputs**
- Test reports
- Diff/golden validation results

---

## Handoff checkpoints
- Stage 0: contract + governance locked
- Stage 1: extraction correctness proven on fixture bundle
- Stage 2: renderer produces ADS docs from MITRE-only
- Stage 3: profiles/overlays safely inject org context
- Stage 4: rule references enrichment (CTID first)
- Stage 5: Task Pack integration

---

## Definition of Done (Stage 0)
- Contract documents exist and are internally consistent.
- Source-of-truth rules are explicit.
- Non-goals and guardrails are explicit.
- Future stages cannot proceed without meeting these constraints.
