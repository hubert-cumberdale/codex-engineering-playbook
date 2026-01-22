# Stage 4 Error Codes (Dataset Validation)

This document defines deterministic error codes for the Stage 4 offline rule-mapping dataset validation.

Principles:
- Errors are explicit and deterministic.
- Validation fails closed unless a code is explicitly marked non-fatal.
- Empty references (no dataset match) are valid and never an error.

---

## Error code definitions

MISSING_REQUIRED_FIELD
- Trigger: A required field is absent in dataset metadata or a dataset row.
- Applies to: `provider`, `rule_id`, `technique_id`/`subtechnique_id`, `dataset_version`, `dataset_hash`, `dataset_bytes`.

EMPTY_REQUIRED_FIELD
- Trigger: A required field is present but empty (e.g., empty string).
- Applies to: `provider`, `rule_id`, `dataset_version`, `dataset_hash`.

INVALID_ATTACK_PATTERN_ID
- Trigger: `technique_id` or `subtechnique_id` does not match the required regex.
- Regex:
  - `technique_id`: `^T[0-9]{4}$`
  - `subtechnique_id`: `^T[0-9]{4}\.[0-9]{3}$`

BOTH_TECHNIQUE_AND_SUBTECHNIQUE
- Trigger: A dataset row includes both `technique_id` and `subtechnique_id`.

MISSING_TECHNIQUE_OR_SUBTECHNIQUE
- Trigger: A dataset row includes neither `technique_id` nor `subtechnique_id`.

HASH_MISMATCH
- Trigger: Computed hash of `dataset_bytes` does not equal `dataset_hash`.

VERSION_MISMATCH
- Trigger: `expected_dataset_version` is provided and does not equal `dataset_version`.

EXPECTED_HASH_MISMATCH
- Trigger: `expected_dataset_hash` is provided and does not equal `dataset_hash`.

ORDERING_INSTABILITY
- Trigger: Provider output order does not preserve dataset source order after de-duplication.

DUPLICATE_REFERENCE (non-fatal)
- Trigger: Multiple rows share the same de-duplication key (`provider` + `rule_id` + `technique_id` or `subtechnique_id`).
- Behavior: Keep the first-seen row; drop subsequent duplicates. Emit this code for each duplicate.

---

## Non-errors
- Unknown fields in dataset rows are ignored and do not raise errors.
- Empty references (no dataset match for a technique/sub-technique) are valid.
