import json
from pathlib import Path

from tools.review import report, run_review
from tools.review.checks import CheckResult, run_checks


def write_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def build_repo_root(tmp_path: Path, include_runbook: bool = True) -> Path:
    for doc in (
        "docs/EXEC_SUMMARY.md",
        "docs/VERSIONING.md",
        "docs/GOVERNANCE.md",
        "docs/Canonical Conventions.md",
        "docs/System Overview.md",
    ):
        write_file(tmp_path / doc)

    (tmp_path / ".codex" / "library").mkdir(parents=True, exist_ok=True)

    taskpack_dir = tmp_path / "taskpacks" / "TASK-0001-sample"
    taskpack_dir.mkdir(parents=True, exist_ok=True)
    required = ["task.yml", "spec.md", "acceptance.yml", "risk.md"]
    if include_runbook:
        required.append("runbook.md")
    for filename in required:
        write_file(taskpack_dir / filename)

    return tmp_path


def test_report_schema_stability() -> None:
    result = CheckResult(
        check_id="repo_layout",
        description="Repo layout",
        status="pass",
        violations=(),
        error=None,
    )
    report_dict = report.build_report("advisory", [result])
    json_text = report.dump_report(report_dict)
    expected = """{
  \"checks\": [
    {
      \"check_id\": \"repo_layout\",
      \"description\": \"Repo layout\",
      \"error\": null,
      \"status\": \"pass\",
      \"violations\": []
    }
  ],
  \"error\": null,
  \"mode\": \"advisory\",
  \"schema_version\": \"1.0\",
  \"status\": \"pass\",
  \"violation_count\": 0
}"""
    assert json_text == expected


def test_checks_positive(tmp_path: Path) -> None:
    repo_root = build_repo_root(tmp_path, include_runbook=True)
    results = run_checks(repo_root)
    assert all(result.status == "pass" for result in results)


def test_strict_mode_violation_exit_code(tmp_path: Path) -> None:
    repo_root = build_repo_root(tmp_path, include_runbook=False)
    report_path = tmp_path / "review_report.json"
    exit_code = run_review.run("strict", repo_root, report_path)
    assert exit_code == 2
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_data["status"] == "violation"
