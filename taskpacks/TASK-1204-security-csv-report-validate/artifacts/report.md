# Coverage Report

## Summary

- Total rows: 6
- Covered: 2
- Partial: 2
- Missing: 2

## By Technique

| Technique | Covered | Partial | Missing |
|---|---:|---:|---:|
| T1027 | 0 | 0 | 1 |
| T1047 | 1 | 1 | 0 |
| T1059 | 1 | 1 | 0 |
| T1110 | 0 | 0 | 1 |

## Detail

| Technique | Control | Status | Owner | Notes |
|---|---|---|---|---|
| T1027 | C-006 | missing | secops | requires parser updates |
| T1047 | C-004 | covered | edr | endpoint rule enabled |
| T1047 | C-005 | partial | edr | coverage limited to Windows |
| T1059 | C-001 | covered | secops | validated via simulation |
| T1059 | C-002 | partial | secops | telemetry present; alert tuning needed |
| T1110 | C-003 | missing | iam | no detections yet |
