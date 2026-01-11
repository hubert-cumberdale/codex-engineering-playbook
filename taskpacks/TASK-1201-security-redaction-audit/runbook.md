# Runbook (local)

## Preconditions
- Python 3.x available.

## Run
From repository root:

```bash
cd taskpacks/TASK-1201-security-redaction-audit
python -m compileall -q src tests tools
python tools/lint_check.py
python -m unittest -q
python tools/make_evidence.py
```

## Expected artifacts
- artifacts/redacted_sample.txt
- artifacts/evidence.json

## Expected output snapshots

### Console output (example)
- `LINT_CHECK_OK`
- `EVIDENCE_WRITTEN artifacts/evidence.json`

### `artifacts/redacted_sample.txt` (excerpt)
```text
User: [REDACTED_EMAIL]
Peer: [REDACTED_EMAIL]
Host: [REDACTED_IPV4]
Note: token=[REDACTED_TOKEN]
Other: ok
```

### `artifacts/evidence.json` (shape + key fields)
- `taskpack_id` = `TASK-1201-security-redaction-audit`
- `inputs.input_sha256` is a 64-char hex string
- `outputs.output_sha256` is a 64-char hex string
- `redaction_counts` includes keys: `email`, `ipv4`, `token`

Example excerpt:
```json
{
  "taskpack_id": "TASK-1201-security-redaction-audit",
  "tool": {"name": "make_evidence.py", "python": "3.12.1"},
  "inputs": {
    "input_sha256": "…",
    "sample_input_path": "src/sample_input.txt"
  },
  "outputs": {
    "redacted_sample_path": "…",
    "output_sha256": "…"
  },
  "redaction_counts": {
    "email": 2,
    "ipv4": 1,
    "token": 1
  }
}
```

## Notes
- No network access is required or used.
- This Task Pack is runnable in isolation.
- Hash values will be stable given stable inputs.
- No secrets are required; sample data is synthetic.