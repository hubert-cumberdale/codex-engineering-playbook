from __future__ import annotations

import argparse
from pathlib import Path
import sys

from tools.review import report
from tools.review.checks import run_checks


def resolve_repo_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parents[2]


def run(mode: str, repo_root: Path, report_path: Path | None) -> int:
    results = run_checks(repo_root)
    result_report = report.build_report(mode, results)

    output_path = report_path or report.default_report_path(repo_root)
    report.write_report(result_report, output_path)

    if result_report["status"] == "error":
        return 1
    if mode == "strict" and result_report["status"] == "violation":
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic review checks runner")
    parser.add_argument(
        "--mode",
        choices=("advisory", "strict"),
        default="advisory",
        help="advisory exits 0 on violations; strict exits 2",
    )
    parser.add_argument(
        "--report-path",
        help="Path to write review_report.json (default uses .orchestrator_logs when present)",
    )
    parser.add_argument(
        "--repo-root",
        help="Override repository root (intended for tests)",
    )

    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)
    report_path = Path(args.report_path).resolve() if args.report_path else None

    try:
        return run(args.mode, repo_root, report_path)
    except Exception as exc:  # pragma: no cover - defensive
        error_report = {
            "schema_version": report.SCHEMA_VERSION,
            "mode": args.mode,
            "status": "error",
            "violation_count": 0,
            "checks": [],
            "error": str(exc),
        }
        output_path = report_path or report.default_report_path(repo_root)
        report.write_report(error_report, output_path)
        return 1


if __name__ == "__main__":
    sys.exit(main())
