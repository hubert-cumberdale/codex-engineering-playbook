# Risk posture

SAFE-by-default. No network. No cloud mutations.

Key risk is import-path plugin loading. Mitigations:
- use importlib with explicit module + symbol parsing
- no eval/exec
- emit clear errors
- keep plugin results free of secrets
