# Web Development Task Pack Template

This template is used for **web development tasks** that change, generate, or validate application code while preserving safety and reproducibility.

---

## When to use this

Use this template for tasks such as:
- API or service scaffolding
- Backend or frontend feature implementation
- Contract or schema enforcement
- Refactors with test coverage
- Build, lint, or static analysis improvements

This template applies to:
- Backend services
- Frontend components
- Shared libraries or tooling

Deployment is **out of scope** unless explicitly declared.

---

## What this template assumes

- **Build-only by default**
  - No deployment
  - No infrastructure mutation
- **Contract-driven development**
  - APIs, schemas, and interfaces are explicit
- **Tests or validation as acceptance**
  - Unit tests, integration tests, schema checks, or build success
- **Incremental change**
  - Small, reviewable diffs
  - No framework rewrites in a single task pack

Network access and environment mutation must be explicitly declared in constraints.

---

## How to instantiate

1. Copy this directory to a new task pack:
```bash
   cp -r taskpacks/_templates/web taskpacks/<TASK-ID>-<slug>
```
2. Update:
- `task.yml`: language, framework context, constraints
- `spec.md`: functional goal and boundaries
- `acceptance.yml`: test, build, or validation criteria
- `risk.md`: regression or compatibility risks
- `runbook.md`: how to build, test, and verify locally
3. Verify:
- The task pack does not assume deployment
- Acceptance is objective and automatable
- Changes are limited to the declared scope

If the task requires live traffic or production state, it does not belong here.