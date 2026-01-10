# Security Task Pack Template

This template is used for **security engineering work** where the goal is to validate, analyze, or improve security posture in a controlled, auditable way.

---

## When to use this

Use this template for tasks such as:
- Detection or control validation
- Security configuration review
- Threat modeling (lightweight)
- Security testing that produces evidence (reports, findings, diffs)
- Continuous validation or posture checks

This template applies whether the task is:
- Tool-based (e.g., scanners, validators), or
- Analysis-based (e.g., reviewing configs, rules, or logic)

BAS / AttackIQ–related work belongs here **as a solution**, not as a special case.

---

## What this template assumes

- **Safety first**
  - No implicit network access
  - No implicit cloud or environment mutation
  - No secrets
- **Evidence-driven outcomes**
  - Artifacts (reports, logs, structured outputs) are the primary result
- **Bounded scope**
  - One security question per task pack
  - No open-ended discovery or exploration
- **Machine-checkable acceptance where possible**
  - Linting, schema validation, diff checks, or assertions

Threat modeling is expected to be *explicit but lightweight*.

---

## How to instantiate

1. Copy this directory to a new task pack:
```bash
   cp -r taskpacks/_templates/security taskpacks/<TASK-ID>-<slug>
```
2. Update:
- `task.yml`: task name, constraints, plugin usage (if any)
- `spec.md`: security objective and scope
- `acceptance.yml`: concrete success criteria
- `risk.md`: risks of change or non-change
- `runbook.md`: how to run and interpret results
3. Verify:
- The task pack runs in isolation
- Acceptance criteria are objective and reviewable
- Artifacts clearly support the acceptance decision

If the task cannot produce evidence, it likely does not belong in this system.