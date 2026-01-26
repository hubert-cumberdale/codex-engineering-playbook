# Instructions (Template)

You are operating on a **managed repository workspace** (NOT this playbook repo).

## Authoritative sources in the target repo
Read these files FIRST and treat them as contracts:
- docs/GOVERNANCE.md
- docs/CURRENT_WORK.md
- (plus any additional Tier-1/Tier-2 docs referenced by the task)

## Rules
- Do not expand scope beyond the task requirements.
- Do not invent new behavior.
- Do not relax safety constraints.
- Keep changes minimal and reviewable.

## Evidence
You MUST:
- run the acceptance commands in `acceptance.yml`
- summarize changes by file
- report test results

If artifacts are produced, document them in `artifacts/README.md` and keep them deterministic.
