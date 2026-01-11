# Risks & mitigations

## Risk: accidental secret disclosure in sample data
Mitigation:
- `src/sample_input.txt` contains synthetic examples only (fake tokens, example IPs/emails).
- Evidence includes hashes, not raw “sensitive” originals.

## Risk: non-deterministic evidence
Mitigation:
- Evidence generation is deterministic:
  - stable ordering
  - no timestamps in evidence payload
  - hashes used for integrity

## Risk: scope creep into “security product”
Mitigation:
- This is a minimal demonstration of evidence-first posture in a Task Pack.
- No runtime agent/service, no integrations.
