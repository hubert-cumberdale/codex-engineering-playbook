# Stage 4 Test Matrix (Machine-Checkable)

This document defines a machine-checkable acceptance test plan for Stage 4 rule-reference enrichment.

Constraints:
- No test implementation.
- No performance testing.

---

## Inputs
All tests use pinned, offline inputs only:
- STIX bundle bytes + hash
- Company profile/overlays (merged hash)
- Dataset bytes + `dataset_version` + `dataset_hash`

---

## Determinism tests
DETERMINISM_SAME_INPUTS
- Given identical inputs (STIX bundle bytes/hash, profile/overlay hash, dataset bytes/version/hash), output must be byte-identical.
- Compare full rendered output bytes, not normalized text.

---

## Negative scope tests
NO_REFERENCES_ON_STRATEGY
- Rule references must not appear in detection strategy sections (non-attack-pattern objects).

NO_REFERENCES_ON_ANALYTIC
- Rule references must not appear in analytic sections (non-attack-pattern objects).

---

## Schema validation tests
INVALID_ATTACK_PATTERN_ID
- Reject rows with malformed `technique_id` or `subtechnique_id`.

DUPLICATE_REFERENCE
- Duplicate reference rows must be de-duplicated (first-seen retained) without reordering.

HASH_MISMATCH
- Reject dataset when computed hash of `dataset_bytes` does not equal `dataset_hash`.

UNKNOWN_FIELDS_IGNORED
- Unknown fields are accepted and ignored; they must not affect output bytes.

---

## Renderer contract tests
NO_NEW_SECTIONS
- Rendered document must include only the 10 required sections; no new top-level sections are introduced.

SECTION_ORDER_UNCHANGED
- Section order must match the contract exactly.

ADDITIVE_ONLY_BLOCK
- Rule references must appear only inside the existing **Additional Resources** section and must not replace existing content.
