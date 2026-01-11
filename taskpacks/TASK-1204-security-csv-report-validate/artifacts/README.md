# Artifacts (evidence)

Acceptance writes deterministic evidence here:

- `report.json` — machine-readable report with:
  - source CSV path + sha256
  - summary counts
  - normalized detail rows
- `report.md` — human-readable markdown report
- `schema_validation.json` — schema validation result (must be `ok`, errors `[]`)

No network access is required or used.
No secrets or credentials are required.
