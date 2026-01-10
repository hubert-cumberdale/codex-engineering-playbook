# Skill: web-acceptance-contracts

## Purpose
Provide a repeatable pattern for writing **command-based acceptance** for web Task Packs.

This skill helps ensure web work is:
- runnable in isolation,
- deterministic under CI,
- evidence-first (artifacts as primary outputs),
- and compliant with v1 safety guarantees (no implicit network or deployment).

## When to use
Use this skill when a Task Pack:
- adds or changes web code (frontend, backend, tooling),
- needs CI-verifiable acceptance (format/lint/test/build),
- requires artifacts to prove a contract (e.g., build output captured as a file).

## When NOT to use
Do not use this skill to:
- add deployment steps,
- require external services by default,
- introduce network access unless explicitly allowed by task constraints,
- describe acceptance in qualitative language (“looks good”, “fast”, “clean UI”).

## Inputs and assumptions
Typical assumptions for web repos (adapt to the project):
- A package manager is present (e.g., npm/pnpm/yarn) OR a Python toolchain (e.g., uv/pip/poetry)
- Lint/test/build commands exist and can run locally
- Acceptance must be **local commands only**
- Any required tooling must be declared in the Task Pack instructions (spec/runbook)

## Acceptance contract patterns

### Pattern A: Format (optional but common)
Goal: enforce stable formatting with a single command.

Examples:
- `npm run format:check`
- `python -m ruff format --check .`

Rules:
- Formatting acceptance should be non-interactive.
- Prefer “check” modes that fail on diff.

### Pattern B: Lint
Goal: fail fast on static issues.

Examples:
- `npm run lint`
- `python -m ruff check .`

Rules:
- Lint must run without network.
- If lint depends on generated files, generate them as part of acceptance explicitly.

### Pattern C: Test
Goal: validate behavior deterministically.

Examples:
- `npm test -- --ci`
- `python -m pytest -q`

Rules:
- Tests should be hermetic where possible.
- If integration tests require services, split them out or gate with explicit constraints.

### Pattern D: Build / contract output (recommended)
Goal: prove the system can produce an expected build artifact (or build summary) deterministically.

Examples:
- `npm run build`
- `python -m build`

Rules:
- Always capture build evidence to the Task Pack `artifacts/` directory when the Task Pack claims a build contract.
- Artifacts should be small and textual when possible (e.g., `build-contract.txt`).

## Evidence-first artifacts

### Artifact expectations
If a Task Pack claims a build contract, produce:
- `taskpacks/<TASK-ID>/artifacts/README.md` describing what evidence is present
- one or more small evidence files (e.g., `build-contract.txt`) that can be validated in CI

### Example artifact: build-contract.txt
Include:
- timestamp (optional)
- command executed
- tool versions (when easy)
- a short summary of outputs (no huge logs)

## Minimal example: acceptance.yml (web build contract)
This is a pattern, not a universal template. Adjust commands to the repo.

```yaml
version: 1
must:
  - name: format
    cmd: npm run format:check
  - name: lint
    cmd: npm run lint
  - name: test
    cmd: npm test -- --ci
  - name: build
    cmd: npm run build
```

## Common failure modes

- Acceptance calls the network implicitly
    - Fix: remove install steps that fetch remote deps during acceptance
    - Prefer vendored lockfiles and deterministic installs outside acceptance if needed
- Build produces large binary artifacts
    - Fix: store a textual “contract” artifact instead (summary output)
- Qualitative acceptance language
    - Fix: rewrite as command outcomes and evidence checks

## Non-goals
- Deployment, hosting, or runtime environment provisioning
- Adding new orchestrator behavior
- Introducing plugin requirements
- Assuming a specific web framework

## See also
- **Skill: web-build-artifact-evidence** — patterns for producing small, deterministic build evidence artifacts that acceptance can validate.
- **TASK-0101-web-build-contract-check** — canonical example of a web Task Pack that combines command-based acceptance with build contract evidence.

---