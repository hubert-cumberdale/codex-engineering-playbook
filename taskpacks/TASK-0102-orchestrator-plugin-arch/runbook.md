# Runbook

## Purpose

Implement the orchestrator plugin architecture and reference plugin per the Task Pack spec.

## How to run

- Run the acceptance commands in `acceptance.yml`.
- No network access or elevated privileges are required.

## Expected output

- Orchestrator plugin modules under `tools/orchestrator/plugins/`.
- Reference plugin under `solutions/security/echo/`.
- Tests validating loader, runner constraints, and artifacts.

## Acceptance

- Acceptance tests pass.
- Plugin loader, runner, and reference plugin exist and behave per spec.
- No orchestrator runtime behavior changes beyond the additive plugin tooling.
