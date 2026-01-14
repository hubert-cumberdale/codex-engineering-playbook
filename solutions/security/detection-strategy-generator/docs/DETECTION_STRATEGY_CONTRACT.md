# Detection Strategy Document Contract (ADS-style)

This contract defines the required structure and invariants for generated detection strategy documents.

The generator produces Palantir-style “Alerting Detection Strategy” Markdown documents, sourced from MITRE ATT&CK detection strategy + analytic STIX objects, and optionally enriched with references-only rule mappings.

---

## 1. Required document structure (10 sections)

Every document MUST contain these sections in this order:

1. **Goal**
2. **Categorization**
3. **Strategy Abstract**
4. **Technical Context**
5. **Blind Spots and Assumptions**
6. **False Positives**
7. **Validation**
8. **Priority**
9. **Response**
10. **Additional Resources**

### Section invariants
- Each section must be present even if content is unknown.
- Unknown/missing content must be explicit (e.g., `TBD`, `Not provided by source`, `Telemetry gap`).

---

## 2. Provenance block (required)
Every document MUST include a provenance block (preferably near the top or bottom) with:

- ATT&CK domain (enterprise/mobile/ics)
- STIX bundle identifier or version pin (tag/commit/hash)
- Hash of the STIX input bundle (or equivalent checksum)
- Generator version (semver)
- Company profile identifier + hash
- Render timestamp (ISO-8601)
- Source object references:
  - Detection Strategy STIX id
  - Detection Strategy external id (e.g., DET####) when present
  - Analytic STIX ids referenced
  - Technique/sub-technique external ids when explicitly linked

If rule enrichment is enabled, provenance MUST also include:
- provider id(s)
- provider dataset/version pin
- provider dataset hash (or checksum)

---

## 3. Determinism rules (required)
Given the same inputs, outputs MUST be identical.

Inputs that define output determinism:
- STIX bundle bytes (or hash)
- company profile + overlays (merged hash)
- template version (hash)
- generator version
- rule provider dataset pin + hash (if enabled)

Non-deterministic operations (network fetch without pinning, random ordering, locale/time-dependent formatting) are prohibited.

---

## 4. Source-grounding rules (required)
The system MUST NOT:
- invent detection logic
- invent telemetry sources
- infer technique mappings if not explicitly present
- claim coverage effectiveness based solely on mappings

Allowed transformations:
- formatting changes (bullets, headings)
- extracting and reordering for readability
- adding explicit placeholders for missing data
- inserting company-owned operational context into dedicated sections (Priority, Response, Validation, local assumptions)

---

## 5. Customization contract (company profile)
The company profile/overlays MAY provide:
- environment truth (telemetry availability and names)
- ownership and escalation routing
- priority rubric and default priority levels
- validation procedures (BAS-oriented)
- links to internal runbooks/playbooks
- known false positives and tuning guidance

The company profile/overlays MUST NOT:
- alter MITRE-derived intent (Goal/Abstract meaning)
- introduce claims of detection capability without evidence
- redefine technique mappings unless explicitly declared as “local mapping”

---

## 6. Rule enrichment contract (references-only)
Rule enrichment is optional and MUST be references-only.

Allowed:
- rule IDs, names, URLs, platforms, status, timestamps, mapping confidence
- mapping provenance and dataset references

Not allowed by default:
- embedding full rule bodies
- translating rule logic into new detection logic text

---

## 7. File naming and identifiers
Recommended path:
- `docs/detection-strategies/<domain>/<DET####>_<slug>.md`

If DET#### is not available, use:
- `docs/detection-strategies/<domain>/ds_<stix-id-short>_<slug>.md`

Slug rules:
- lowercase
- hyphen-separated
- alphanumeric + hyphen only

---

## 8. Compatibility with ASM / CTEM / BAS
The doc must support:
- ASM: explicit telemetry requirements and gaps
- CTEM: provenance and determinism for auditability
- BAS: validation section that can be operationalized (even if scaffolded)
