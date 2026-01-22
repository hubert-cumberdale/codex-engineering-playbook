# Stage 4 Renderer Attachment Rules

This document defines how Stage 4 rule references are placed in rendered Markdown.

---

## Placement
- Rule references attach only to `attack-pattern` techniques/sub-techniques.
- Attachments MUST appear within the existing **Additional Resources** section of the owning object.
- Do NOT add or rename top-level sections.

---

## Labeling
Each rule-reference block MUST include the label:

`Source: Offline CTID mapping dataset`

(Exact text required to ensure consistent provenance visibility.)

---

## Provenance display
Within the Additional Resources section, display dataset provenance alongside rule references:

- `provider_id`
- `dataset_version`
- `dataset_hash`

Provenance must be visible in the rendered document and must not be hidden in comments.

---

## Coexistence with Additional Resources
- Rule references are additive and must not replace or restructure existing Additional Resources content.
- When Additional Resources already exists, append rule references after existing entries in source order.
- Do not introduce summaries, counts, or rollups.
