# Stage 4 Acceptance Criteria

Stage 4 is accepted only if all criteria below are met.

---

## Determinism
- Given identical inputs (STIX bundle, profile/overlays, dataset bytes, dataset version/hash), outputs are byte-identical.
- No network access or time-dependent formatting affects output.

---

## No semantic drift
- MITRE-derived content remains unchanged beyond formatting and explicit placeholders.
- Rule references do not alter meaning of Goal, Abstract, or Technical Context sections.

---

## No aggregation
- No rollups, counts, summaries, or inferred effectiveness.
- Rule references are listed as discrete items only.

---

## Correct scoping
- Attachments only target `attack-pattern` techniques/sub-techniques.
- No attachments to detection strategies, analytics, or other STIX objects.
- No relationship traversal to infer additional mappings.

---

## Provenance visibility
- Provider identity, dataset version, and dataset hash are visible in rendered output.
- Required label `Source: Offline CTID mapping dataset` is present.

---

## Renderer contract preserved
- The 10 required sections and their order remain unchanged.
- Rule references appear only inside the existing **Additional Resources** section.
- No new top-level sections are introduced.
