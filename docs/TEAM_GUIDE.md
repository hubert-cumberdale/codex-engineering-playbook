# TEAM_GUIDE.md

> This document provides operational guidance for contributors.
> Authoritative system behavior and guarantees are defined under `/docs`.

## Commands
- Setup (uv): `uv sync --dev`
- Tests: `uv run pytest -q`
- Deterministic review (advisory): `PYTHONPATH=. uv run python -m tools.review.run_review --mode advisory --report-path review_report.json`
- Install pre-push review hook (opt-in): `./scripts/install-pre-push-hook.sh`

## Conventions
- Task Packs live in `taskpacks/`
- Skills live in `.codex/skills/`
- Orchestrator runs locally and via GitHub Actions
- For v1.2 non-blocking hygiene patterns (determinism, evidence surfaces, Python import posture), see `docs/v1.2/HYGIENE_GUIDANCE.md` (Tier-2).

See `CHAT_PLAYBOOK.md` for how ChatGPT is used in this project.
