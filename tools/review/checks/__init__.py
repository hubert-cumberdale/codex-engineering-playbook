from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from tools.review.checks import repo_layout, taskpack_contracts


@dataclass(frozen=True)
class Check:
    check_id: str
    description: str
    run: Callable[[Path], list[str]]


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    description: str
    status: str
    violations: tuple[str, ...]
    error: str | None


CHECKS: tuple[Check, ...] = (
    Check(
        check_id="repo_layout",
        description="Required repo layout artifacts exist",
        run=repo_layout.check,
    ),
    Check(
        check_id="taskpack_contracts",
        description="Taskpack required files exist",
        run=taskpack_contracts.check,
    ),
)


def run_checks(repo_root: Path, checks: Iterable[Check] | None = None) -> list[CheckResult]:
    selected_checks = list(checks or CHECKS)
    results: list[CheckResult] = []

    for check in sorted(selected_checks, key=lambda item: item.check_id):
        try:
            violations = sorted(check.run(repo_root))
            status = "pass" if not violations else "violation"
            results.append(
                CheckResult(
                    check_id=check.check_id,
                    description=check.description,
                    status=status,
                    violations=tuple(violations),
                    error=None,
                )
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                CheckResult(
                    check_id=check.check_id,
                    description=check.description,
                    status="error",
                    violations=(),
                    error=str(exc),
                )
            )

    return results
