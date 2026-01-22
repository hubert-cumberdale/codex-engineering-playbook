# Stage 4 Provider Interface (Rule References)

This document defines the required interface for Stage 4 rule-reference providers.

---

## Purpose
Attach references-only rule metadata to ATT&CK techniques/sub-techniques without changing renderer structure or STIX traversal.

---

## Required inputs
Provider interface inputs are explicit and immutable for a single run:

- `provider_id` (string, required)
- `dataset_version` (string, required)
- `dataset_hash` (string, required; cryptographic hash of dataset bytes)
- `dataset_bytes` (bytes, required; offline/pinned dataset content)
- `attack_techniques` (list of ATT&CK technique/sub-technique external IDs present in the normalized model; required)

No network access or external lookups are permitted.

---

## Required outputs
The provider returns a deterministic, ordered collection of rule references scoped to techniques/sub-techniques.

Per reference:
- `provider` (string, required; must match `provider_id`)
- `rule_id` (string, required)
- `technique_id` or `subtechnique_id` (string, required; exactly one)
- `display_name` (string, optional)
- `url` (string, optional)

Dataset-level provenance (required):
- `provider_id`
- `dataset_version`
- `dataset_hash`

The provider MUST NOT invent or infer mappings beyond the dataset content.

---

## Determinism rules
- Output ordering preserves dataset source order (first-seen wins on dedupe).
- Identical inputs MUST produce byte-identical outputs.
- Locale, timestamps, and randomization MUST NOT affect output.

---

## Errors
Provider must fail closed with explicit errors:

- Missing required fields (`provider_id`, `dataset_version`, `dataset_hash`, `dataset_bytes`).
- Invalid or empty `rule_id` / `technique_id` / `subtechnique_id`.
- Rows that specify both `technique_id` and `subtechnique_id`.
- Dataset hash mismatch (when an expected hash is supplied).
- Non-deterministic ordering changes introduced by provider logic.

---

## Provenance requirements
Every rendering that includes rule references must display:

- `provider_id`
- `dataset_version`
- `dataset_hash`
- Label indicating offline/pinned source

Provenance must be visible in the rendered document and preserved in any internal manifests.
