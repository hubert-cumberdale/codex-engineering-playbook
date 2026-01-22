from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from tools.review.checks import CheckResult

SCHEMA_VERSION = "1.0"


def build_report(mode: str, check_results: Iterable[CheckResult]) -> dict:
    results = list(check_results)
    violation_count = sum(len(result.violations) for result in results if result.status == "violation")
    status = "pass"
    if any(result.status == "error" for result in results):
        status = "error"
    elif violation_count > 0:
        status = "violation"

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "status": status,
        "violation_count": violation_count,
        "error": None,
        "checks": [
            {
                "check_id": result.check_id,
                "description": result.description,
                "status": result.status,
                "violations": list(result.violations),
                "error": result.error,
            }
            for result in results
        ],
    }


def dump_report(report: dict) -> str:
    return json.dumps(report, sort_keys=True, indent=2)


def default_report_path(repo_root: Path) -> Path:
    orchestrator_logs = repo_root / ".orchestrator_logs"
    if orchestrator_logs.is_dir():
        return orchestrator_logs / "review_report.json"
    return repo_root / "review_report.json"


def write_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_report(report) + "\n", encoding="utf-8")
