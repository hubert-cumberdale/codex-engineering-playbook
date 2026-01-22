#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Callable, Iterable

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

SCHEMA_VERSION = 1
TOOL_NAME = "tools.review.run_review"
TOOL_VERSION = "unknown"

CATEGORY_DOCS = "docs"
CATEGORY_TASKPACK = "taskpack"
CATEGORY_REPO = "repo"
CATEGORY_TOOLING = "tooling"

ALLOWED_CATEGORIES = {
    CATEGORY_DOCS,
    CATEGORY_TASKPACK,
    CATEGORY_REPO,
    CATEGORY_TOOLING,
}

ALLOWED_SEVERITIES = {"error", "warn"}

RULE_DOCS_TIER1_MISSING = "DOCS_TIER1_MISSING"
RULE_DOCS_RELEASE_NOTES_DIR_MISSING = "DOCS_RELEASE_NOTES_DIR_MISSING"
RULE_DOCS_RELEASE_NOTES_MISSING = "DOCS_RELEASE_NOTES_MISSING"
RULE_TASKPACK_DIR_MISSING = "TASKPACK_DIR_MISSING"
RULE_TASKPACK_FILE_MISSING = "TASKPACK_FILE_MISSING"


def build_violation(
    violation_id: str,
    *,
    category: str,
    severity: str,
    message: str,
    path: str,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"unknown violation category: {category}")
    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(f"unknown violation severity: {severity}")

    violation: dict[str, object] = {
        "id": violation_id,
        "category": category,
        "severity": severity,
        "message": message,
        "path": path,
    }
    if details is not None:
        violation["details"] = details
    return violation


def sort_violations(violations: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        violations,
        key=lambda v: (
            str(v.get("id", "")),
            str(v.get("path", "")),
            str(v.get("message", "")),
        ),
    )


def rfc3339_utc_now() -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return timestamp.replace("+00:00", "Z")


def check_tier1_docs(root: Path) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []

    for rel_path in TIER1_FILES:
        if not (root / rel_path).is_file():
            violations.append(
                build_violation(
                    RULE_DOCS_TIER1_MISSING,
                    category=CATEGORY_DOCS,
                    severity="error",
                    message="missing required Tier 1 document",
                    path=rel_path,
                )
            )

    releases_dir = root / RELEASE_NOTES_DIR
    if not releases_dir.is_dir():
        violations.append(
            build_violation(
                RULE_DOCS_RELEASE_NOTES_DIR_MISSING,
                category=CATEGORY_DOCS,
                severity="error",
                message="missing release notes directory",
                path=RELEASE_NOTES_DIR,
            )
        )
        return violations

    release_notes = sorted(releases_dir.glob(RELEASE_NOTES_GLOB))
    if not release_notes:
        violations.append(
            build_violation(
                RULE_DOCS_RELEASE_NOTES_MISSING,
                category=CATEGORY_DOCS,
                severity="error",
                message="no release notes files found",
                path=RELEASE_NOTES_DIR,
            )
        )

    return violations


def check_taskpack_structure(root: Path) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    taskpacks_root = root / "taskpacks"
    if not taskpacks_root.is_dir():
        violations.append(
            build_violation(
                RULE_TASKPACK_DIR_MISSING,
                category=CATEGORY_TASKPACK,
                severity="error",
                message="missing taskpacks directory",
                path="taskpacks",
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
                        RULE_TASKPACK_FILE_MISSING,
                        category=CATEGORY_TASKPACK,
                        severity="error",
                        message="missing required taskpack file",
                        path=rel_path,
                    )
                )

    return violations


CHECKS: list[Callable[[Path], list[dict[str, object]]]] = [
    check_tier1_docs,
    check_taskpack_structure,
]


def generate_report(root: Path, mode: str) -> dict[str, object]:
    violations: list[dict[str, object]] = []
    for check in CHECKS:
        violations.extend(check(root))

    sorted_violations = sort_violations(violations)
    status = "pass" if not sorted_violations else "fail"

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": rfc3339_utc_now(),
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "mode": mode,
        "summary": {
            "checks": len(CHECKS),
            "violations": len(sorted_violations),
            "status": status,
        },
        "root": root.resolve().as_posix(),
        "violations": sorted_violations,
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
