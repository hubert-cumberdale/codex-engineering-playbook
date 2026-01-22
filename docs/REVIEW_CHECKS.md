# Review Checks

The review checks are deterministic, repo-defined validations that produce auditable reports.
They are **not** a linter and **not** an AI system. The checks are advisory by default and
only hard-fail on objective rule violations.

## What They Do
- Enforce repo scope and boundary rules using path-based checks.
- Require Tier-1 docs to exist when scoped areas change.
- Run deterministic acceptance checks (compileall + pytest).
- Run existing acceptance tooling for forbidden language on the changed file set.
- Emit a human-readable report to stdout and (optionally) a file.

## What They Do Not Do
- No semantic inference or heuristics.
- No network access.
- No orchestrator behavior changes.

## Run Locally
Fast mode (default):

```bash
python tools/review/run_review_checks.py --fast
```

Full mode:

```bash
python tools/review/run_review_checks.py --full
```

Optional report output:

```bash
python tools/review/run_review_checks.py --full --report-file .review/review_checks_report.txt
```

## Fast vs Full
- `--fast` runs compileall, a minimal pytest subset, and acceptance checks.
- `--full` runs the entire pytest suite plus the same deterministic checks.

## Pre-Push Hook
Install the opt-in hook:

```bash
./scripts/install-pre-push-hook.sh
```

The hook runs:

```bash
python tools/review/run_review_checks.py --fast
```

Bypass (discouraged):
- `SKIP_REVIEW_CHECKS=1 git push`
- `git push --no-verify`

Uninstall:

```bash
rm .git/hooks/pre-push
```

## CI Behavior
The GitHub Actions workflow `review-checks` runs:

```bash
python tools/review/run_review_checks.py --full --report-file .review/review_checks_report.txt
```

It uploads `.review/review_checks_report.txt` as an artifact whether the job passes or fails.

## Difference From Acceptance Tests
Acceptance tests validate task pack behavior. Review checks are repo-wide guardrails that
produce deterministic, auditable reports and reuse existing acceptance tools where applicable.
