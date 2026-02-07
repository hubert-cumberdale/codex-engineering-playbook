from __future__ import annotations

import json
from pathlib import Path

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
        "schema_version",
        "generated_at",
        "tool",
        "mode",
        "summary",
        "root",
        "violations",
    ]
    assert list(report["summary"].keys()) == ["checks", "violations", "status"]

    assert_sorted_keys(
        report_text,
        ["generated_at", "mode", "root", "schema_version", "summary", "tool", "violations"],
    )

    assert report["schema_version"] == 1
    assert report["tool"]["name"] == "tools.review.run_review"
    assert report["tool"]["version"] == "unknown"
    assert report["summary"]["checks"] == len(run_review.CHECKS)
    assert report["summary"]["violations"] == 2
    assert report["summary"]["status"] == "fail"
    assert report["generated_at"].endswith("Z")
    dt = run_review.dt.datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00"))
    assert dt.tzinfo is not None

    for violation in report["violations"]:
        assert set(violation.keys()) == {"id", "category", "severity", "message", "path"}

    assert report["violations"] == [
        {
            "id": run_review.RULE_DOCS_TIER1_MISSING,
            "category": run_review.CATEGORY_DOCS,
            "severity": "error",
            "message": "missing required Tier 1 document",
            "path": missing_tier1,
        },
        {
            "id": run_review.RULE_TASKPACK_FILE_MISSING,
            "category": run_review.CATEGORY_TASKPACK,
            "severity": "error",
            "message": "missing required taskpack file",
            "path": missing_taskpack,
        },
    ]


def test_violation_sorting_is_deterministic() -> None:
    violations = [
        run_review.build_violation(
            "B_RULE",
            category=run_review.CATEGORY_DOCS,
            severity="error",
            message="b-message",
            path="b/path.txt",
        ),
        run_review.build_violation(
            "A_RULE",
            category=run_review.CATEGORY_DOCS,
            severity="error",
            message="z-message",
            path="b/path.txt",
        ),
        run_review.build_violation(
            "A_RULE",
            category=run_review.CATEGORY_DOCS,
            severity="error",
            message="a-message",
            path="a/path.txt",
        ),
    ]

    sorted_violations = run_review.sort_violations(violations)
    assert [v["id"] for v in sorted_violations] == ["A_RULE", "A_RULE", "B_RULE"]
    assert [v["path"] for v in sorted_violations] == ["a/path.txt", "b/path.txt", "b/path.txt"]
    assert [v["message"] for v in sorted_violations] == [
        "a-message",
        "z-message",
        "b-message",
    ]


def test_positive_case(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    report_path = tmp_path / "report.json"

    exit_code = run_review.run_review(tmp_path, "strict", report_path)
    assert exit_code == 0

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["violations"] == 0
    assert report["summary"]["status"] == "pass"
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
    assert report["summary"]["status"] == "fail"
    assert report["violations"] == [
        {
            "id": run_review.RULE_TASKPACK_FILE_MISSING,
            "category": run_review.CATEGORY_TASKPACK,
            "severity": "error",
            "message": "missing required taskpack file",
            "path": "taskpacks/TASK-EXAMPLE/acceptance.yml",
        }
    ]
