# TEAM_GUIDE.md

> This document provides operational guidance for contributors.
> Authoritative system behavior and guarantees are defined under `/docs`.

## Commands
- Tests: `python -m pytest -q`

## Conventions
- Task Packs live in `taskpacks/`
- Skills live in `.codex/skills/`
- Orchestrator runs locally and via GitHub Actions
- For v1.2 non-blocking hygiene patterns (determinism, evidence surfaces, Python import posture), see `docs/v1.2/HYGIENE_GUIDANCE.md` (Tier-2).

See `CHAT_PLAYBOOK.md` for how ChatGPT is used in this project.
