from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.review import run_review


def write_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def create_minimal_repo(root: Path) -> None:
    for rel_path in run_review.TIER1_FILES:
        write_file(root / rel_path)
    write_file(root / "docs/releases/RELEASE_NOTES_v1.0.0.md")

    taskpack_dir = root / "taskpacks" / "TASK-EXAMPLE"
    for filename in run_review.REQUIRED_TASKPACK_FILES:
        write_file(taskpack_dir / filename)


def assert_sorted_keys(json_text: str, keys: list[str]) -> None:
    positions = [json_text.index(f"\"{key}\"") for key in keys]
    assert positions == sorted(positions)


def test_report_schema_stability(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    missing_tier1 = "docs/EXEC_SUMMARY.md"
    missing_taskpack = "taskpacks/TASK-EXAMPLE/risk.md"
    (tmp_path / missing_tier1).unlink()
    (tmp_path / missing_taskpack).unlink()

    report = run_review.generate_report(tmp_path, "advisory")
    report_text = run_review.serialize_report(report)

    assert list(report.keys()) == [
        "mode",
        "root",
        "schema_version",
        "summary",
        "violations",
    ]
    assert list(report["summary"].keys()) == ["checks_run", "violations"]

    assert_sorted_keys(
        report_text,
        ["mode", "root", "schema_version", "summary", "violations"],
    )

    violation_keys = ["check_id", "message", "path"]
    for violation in report["violations"]:
        assert list(violation.keys()) == violation_keys

    assert report["violations"] == [
        {
            "check_id": run_review.CHECK_ID_TIER1,
            "message": "missing required Tier 1 document",
            "path": missing_tier1,
        },
        {
            "check_id": run_review.CHECK_ID_TASKPACK,
            "message": "missing required taskpack file",
            "path": missing_taskpack,
        },
    ]


def test_positive_case(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    report_path = tmp_path / "report.json"

    exit_code = run_review.run_review(tmp_path, "strict", report_path)
    assert exit_code == 0

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["violations"] == 0
    assert report["violations"] == []


def test_negative_case_missing_taskpack_file(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    missing_path = tmp_path / "taskpacks/TASK-EXAMPLE/acceptance.yml"
    missing_path.unlink()
    report_path = tmp_path / "report.json"

    exit_code = run_review.run_review(tmp_path, "advisory", report_path)
    assert exit_code == 2

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["violations"] == 1
    assert report["violations"] == [
        {
            "check_id": run_review.CHECK_ID_TASKPACK,
            "message": "missing required taskpack file",
            "path": "taskpacks/TASK-EXAMPLE/acceptance.yml",
        }
    ]
