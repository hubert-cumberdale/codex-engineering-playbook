# Stage 4 Renderer Attachment Rules

This document defines how Stage 4 rule references are placed in rendered Markdown.

---

## Placement
- Rule references attach only to `attack-pattern` techniques/sub-techniques.
- Attachments MUST appear within the existing **Additional Resources** section of the owning object.
- Do NOT add or rename top-level sections.
- Do not render rule references for non-`attack-pattern` sections (strategies, analytics, or metadata).
- Do not allow cross-scope visibility (a technique’s references must not appear under other techniques).

---

## Labeling
Each rule-reference block MUST include a distinct label:

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

---

## Non-normative example (plain text)
Additional Resources:
Other links...

Source: Offline CTID mapping dataset
provider_id: example-provider
dataset_version: 2026-01-15
dataset_hash: 7f2d2c8e5a0b...
- Rule: RULE-1234 (T1059)
- Rule: RULE-7788 (T1059.003)
