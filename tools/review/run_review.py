#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

TIER1_FILES = [
    "docs/System Overview.md",
    "docs/Architecture & Roadmap.md",
    "docs/Current Status.md",
    "docs/Skill Backlog.md",
    "docs/Canonical Conventions.md",
    "docs/EXEC_SUMMARY.md",
    "docs/GOVERNANCE.md",
    "docs/VERSIONING.md",
    "docs/CHAT_PLAYBOOK.md",
    "docs/TEAM_GUIDE.md",
]

RELEASE_NOTES_DIR = "docs/releases"
RELEASE_NOTES_GLOB = "RELEASE_NOTES_*.md"

REQUIRED_TASKPACK_FILES = [
    "task.yml",
    "spec.md",
    "acceptance.yml",
    "risk.md",
    "runbook.md",
]

CHECK_ID_TIER1 = "tier1_docs_presence"
CHECK_ID_TASKPACK = "taskpack_structure_presence"


def build_violation(check_id: str, path: str, message: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "message": message,
        "path": path,
    }


def check_tier1_docs(root: Path) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []

    for rel_path in TIER1_FILES:
        if not (root / rel_path).is_file():
            violations.append(
                build_violation(
                    CHECK_ID_TIER1,
                    rel_path,
                    "missing required Tier 1 document",
                )
            )

    releases_dir = root / RELEASE_NOTES_DIR
    if not releases_dir.is_dir():
        violations.append(
            build_violation(
                CHECK_ID_TIER1,
                RELEASE_NOTES_DIR,
                "missing release notes directory",
            )
        )
        return violations

    release_notes = sorted(releases_dir.glob(RELEASE_NOTES_GLOB))
    if not release_notes:
        violations.append(
            build_violation(
                CHECK_ID_TIER1,
                RELEASE_NOTES_DIR,
                "no release notes files found",
            )
        )

    return violations


def check_taskpack_structure(root: Path) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    taskpacks_root = root / "taskpacks"
    if not taskpacks_root.is_dir():
        violations.append(
            build_violation(
                CHECK_ID_TASKPACK,
                "taskpacks",
                "missing taskpacks directory",
            )
        )
        return violations

    taskpack_dirs = sorted(
        [p for p in taskpacks_root.iterdir() if p.is_dir() and p.name.startswith("TASK-")],
        key=lambda p: p.name,
    )
    for taskpack_dir in taskpack_dirs:
        for filename in REQUIRED_TASKPACK_FILES:
            rel_path = f"taskpacks/{taskpack_dir.name}/{filename}"
            if not (taskpack_dir / filename).is_file():
                violations.append(
                    build_violation(
                        CHECK_ID_TASKPACK,
                        rel_path,
                        "missing required taskpack file",
                    )
                )

    return violations


CHECKS: list[Callable[[Path], list[dict[str, str]]]] = [
    check_tier1_docs,
    check_taskpack_structure,
]


def generate_report(root: Path, mode: str) -> dict[str, object]:
    violations: list[dict[str, str]] = []
    for check in CHECKS:
        violations.extend(check(root))

    report = {
        "mode": mode,
        "root": root.resolve().as_posix(),
        "schema_version": 1,
        "summary": {
            "checks_run": len(CHECKS),
            "violations": len(violations),
        },
        "violations": violations,
    }
    return report


def serialize_report(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def write_report(report_text: str, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")


def run_review(root: Path, mode: str, report_path: Path) -> int:
    report = generate_report(root, mode)
    report_text = serialize_report(report)
    write_report(report_text, report_path)

    violations = report["summary"]["violations"]
    print(f"review: mode={mode} violations={violations} report={report_path.as_posix()}")
    return 2 if violations else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic review checks runner")
    parser.add_argument(
        "--mode",
        choices=["advisory", "strict"],
        default="advisory",
        help="Run mode (affects report metadata only)",
    )
    parser.add_argument(
        "--report-path",
        default="review-report.json",
        help="Path to write JSON report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return run_review(Path.cwd(), args.mode, Path(args.report_path))
    except Exception as exc:  # pragma: no cover - defensive error path
        print(f"review: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
