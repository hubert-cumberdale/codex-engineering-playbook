# Stage 4 Dataset Schema (CTID Rule Mappings)

This document defines the minimal schema and validation rules for the Stage 4 offline rule-mapping dataset.

---

## Record fields
Each dataset row represents exactly one rule-to-technique mapping.

Required fields:
- `provider` (string; rule provider identifier)
- `rule_id` (string)
- `technique_id` (string) OR `subtechnique_id` (string) — exactly one required

Optional fields:
- `display_name` (string)
- `url` (string)

---

## Field constraints
- `provider` and `rule_id` MUST be non-empty strings.
- `technique_id` MUST match `T####` (e.g., `T1059`).
- `subtechnique_id` MUST match `T####.###` (e.g., `T1059.003`).
- `technique_id` and `subtechnique_id` MUST NOT both be present in the same row.
- If `subtechnique_id` is present, the system MUST NOT infer or add a parent `technique_id`.

---

## Validation rules
- Reject rows missing any required field.
- Reject rows with malformed ATT&CK IDs.
- Reject rows containing both `technique_id` and `subtechnique_id`.
- Ignore unknown fields; do not transform or infer content from them.

---

## Dataset metadata (version + hash)
The dataset MUST be pinned and recorded with:

- `dataset_version` (string)
- `dataset_hash` (cryptographic hash of the dataset bytes)

These values must be captured in provenance and used for determinism checks.

---

## Ordering and dedupe
- Preserve dataset source order exactly.
- If duplicate mappings exist, keep the first-seen row and drop subsequent duplicates.
- Dedupe MUST be stable and MUST NOT reorder records.

---

## No parent inference
Sub-technique mappings are terminal. No parent technique, analytic, or strategy relationships may be inferred or traversed based on the dataset.
