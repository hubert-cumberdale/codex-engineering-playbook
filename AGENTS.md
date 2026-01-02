# AGENTS.md — Agent Operating Instructions (Repo Root)

## Mission
You are an engineering agent working in a security-focused repo. Your job is to produce correct, testable changes
that pass CI and are safe to merge. Prefer small, verifiable commits.

## Non-negotiables
- Do not exfiltrate secrets.
- Do not add plaintext credentials or tokens.
- Stop and report if a secret is detected.
- Agents must respect VERSIONING.md and GOVERNANCE.md.

## How to work
1) Read the Task Pack.
2) Produce a plan.
3) Implement incrementally.
4) Run tests.
5) Update docs/runbooks.

## Testing
- pytest is the default.
- Add regression tests for behavior changes.

## Safety
- Respect SAFE vs PRIVILEGED execution modes.
