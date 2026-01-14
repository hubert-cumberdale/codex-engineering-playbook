# Skills: Detection Strategy Generator

This document defines “skills” (capabilities) the system will implement in later stages.
Stage 0 defines only the interfaces and contracts, not code.

---

## Skill: fetch_attack_stix
**Purpose**
Obtain a specific (pinned) ATT&CK STIX bundle for a chosen domain.

**Inputs**
- domain: `enterprise-attack` | `ics-attack` | `mobile-attack`
- version pin (tag/commit/hash) OR `latest` (explicit opt-in)
- cache_dir

**Outputs**
- local STIX bundle path
- bundle metadata (hash, timestamp, source)

**Constraints**
- Default must be pinned for determinism.
- `latest` must record resolved version + hash.

---

## Skill: parse_detection_strategies
**Purpose**
Extract normalized detection strategies and analytics from the STIX bundle.

**Inputs**
- STIX bundle

**Outputs**
- list of DetectionStrategyRecord objects
- per-record provenance (stix ids, external ids, domains, refs)

**Constraints**
- No inference: missing fields remain missing.
- Preserve raw source references.

---

## Skill: resolve_technique_links
**Purpose**
Associate detection strategies/analytics with techniques/sub-techniques where relationships exist.

**Inputs**
- normalized records
- STIX relationship graph

**Outputs**
- technique refs (Txxxx / Txxxx.yyy)
- confidence: `explicit` only (no heuristic linking in v1)

**Constraints**
- Do not guess technique mapping.

---

## Skill: load_company_profile
**Purpose**
Load and validate org configuration; merge overlays deterministically.

**Inputs**
- profile.yml
- overlays directory (optional)

**Outputs**
- merged profile object
- merged profile hash
- telemetry availability matrix
- ownership/routing config

**Constraints**
- Schema validation required.
- Merges are deterministic and ordered:
  global defaults → platform overlays → strategy overlays.

---

## Skill: render_ads_markdown
**Purpose**
Render ADS-style Markdown detection strategy docs using templates.

**Inputs**
- normalized strategy record
- merged profile
- templates version
- renderer settings

**Outputs**
- markdown doc
- provenance block
- per-doc generation manifest entry

**Constraints**
- Must produce exactly the 10 required ADS sections.
- Unknown data is explicit; no silent omission.
- Must embed provenance and generation metadata.

---

## Skill: enrich_with_rule_refs
**Purpose**
Attach references-only detection rule mappings by technique/sub-technique.

**Inputs**
- technique refs
- configured providers

**Outputs**
- list of RuleRef entries:
  - provider id
  - external reference or URL
  - platform/tool
  - last_updated (if provided)
  - mapping confidence (from provider)

**Constraints**
- References-only: do not embed full rule bodies by default.
- Must embed provider provenance and dataset/version hash.

---

## Skill: validate_contract
**Purpose**
Verify generated docs satisfy contract invariants.

**Inputs**
- generated markdown docs
- manifests
- contract rules

**Outputs**
- pass/fail report
- actionable errors (missing sections, missing provenance, non-determinism)

**Constraints**
- Failing contract blocks release/merge.
