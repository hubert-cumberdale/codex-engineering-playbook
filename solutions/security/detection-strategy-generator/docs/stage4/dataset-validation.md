# Stage 4 Dataset Validation (CTID Rule Mappings)

This document defines validation rules and failure conditions for the Stage 4 offline rule-mapping dataset.

Constraints:
- No inference beyond the dataset content.
- No external lookups.
- No renderer changes.

---

## Scope
Validation applies to:
- Dataset metadata (`dataset_version`, `dataset_hash`, and `dataset_bytes`).
- Dataset rows describing rule-to-technique/sub-technique mappings.
- Provider output ordering and de-duplication behavior.

Validation does not alter or enrich dataset content.

---

## Inputs
Required inputs:
- `dataset_version` (string; non-empty)
- `dataset_hash` (string; cryptographic hash of dataset bytes)
- `dataset_bytes` (bytes; the dataset content)
- `rows` (parsed records from `dataset_bytes`)

Optional pinned values (when supplied by the caller):
- `expected_dataset_version` (string)
- `expected_dataset_hash` (string)

---

## Record field rules (per row)
Required fields:
- `provider` (string; non-empty)
- `rule_id` (string; non-empty)
- Exactly one of:
  - `technique_id`
  - `subtechnique_id`

Optional fields:
- `display_name` (string)
- `url` (string)

Unknown fields:
- Allowed but ignored.
- Unknown fields MUST NOT affect behavior or output.

---

## ATT&CK ID validation
- `technique_id` must match `^T[0-9]{4}$`.
- `subtechnique_id` must match `^T[0-9]{4}\.[0-9]{3}$`.
- `technique_id` and `subtechnique_id` MUST NOT both be present in the same row.
- If `subtechnique_id` is present, no parent technique may be inferred or added.

---

## Metadata validation
- `dataset_version` must be a non-empty string.
- `dataset_hash` must be a non-empty string.
- `dataset_hash` MUST match the cryptographic hash of `dataset_bytes`.
- If `expected_dataset_version` is provided, it MUST equal `dataset_version`.
- If `expected_dataset_hash` is provided, it MUST equal `dataset_hash`.

---

## Duplicates
Duplicate detection key:
- `provider` + `rule_id` + (`technique_id` or `subtechnique_id`)

Rules:
- Keep the first-seen row.
- Drop subsequent duplicates.
- Dedupe MUST be stable and MUST NOT reorder records.

---

## Ordering stability
- Output ordering MUST preserve dataset source order after de-duplication.
- Any ordering changes introduced by provider logic are invalid.

---

## Empty references are valid
If no dataset rows match a technique/sub-technique, the references list for that target is empty.
This is valid and MUST NOT be treated as an error.
