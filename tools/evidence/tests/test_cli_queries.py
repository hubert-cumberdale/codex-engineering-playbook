from __future__ import annotations

import json
from pathlib import Path

from tools.evidence import cli


def write_index(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sample_index() -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2025-01-01T00:00:00Z",
        "roots_scanned": [".orchestrator_logs"],
        "runs": [
            {
                "run_id": "run-b",
                "run_dir": ".orchestrator_logs/run-b",
                "manifest_path": ".orchestrator_logs/run-b/manifest.json",
                "artifacts": [
                    {
                        "type": "review_report",
                        "path": ".orchestrator_logs/run-b/review_report.json",
                        "schema_version": 1,
                    },
                    {
                        "type": "review_report",
                        "path": ".orchestrator_logs/run-b/review_report_copy.json",
                        "schema_version": 1,
                    },
                    {
                        "type": "manifest",
                        "path": ".orchestrator_logs/run-b/manifest.json",
                        "schema_version": None,
                    },
                ],
            },
            {
                "run_id": "run-a",
                "run_dir": ".orchestrator_logs/run-a",
                "manifest_path": ".orchestrator_logs/run-a/manifest.json",
                "artifacts": [
                    {
                        "type": "manifest",
                        "path": ".orchestrator_logs/run-a/manifest.json",
                        "schema_version": None,
                    }
                ],
            },
            {
                "run_id": "run-empty",
                "run_dir": ".orchestrator_logs/run-empty",
                "manifest_path": ".orchestrator_logs/run-empty/manifest.json",
                "artifacts": [],
            },
        ],
    }


def test_list_runs_stdout_ordering(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(["list-runs", "--index", str(index_path)])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "run-a\t.orchestrator_logs/run-a",
        "run-b\t.orchestrator_logs/run-b",
        "run-empty\t.orchestrator_logs/run-empty",
    ]


def test_list_artifacts_stdout_ordering(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(["list-artifacts", "--index", str(index_path), "--run-id", "run-b"])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "manifest\t.orchestrator_logs/run-b/manifest.json\t-",
        "review_report\t.orchestrator_logs/run-b/review_report.json\t1",
        "review_report\t.orchestrator_logs/run-b/review_report_copy.json\t1",
    ]


def test_show_artifact_success(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(
        [
            "show-artifact",
            "--index",
            str(index_path),
            "--run-id",
            "run-a",
            "--type",
            "manifest",
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert captured.out.strip() == ".orchestrator_logs/run-a/manifest.json"


def test_show_artifact_ambiguous(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(
        [
            "show-artifact",
            "--index",
            str(index_path),
            "--run-id",
            "run-b",
            "--type",
            "review_report",
        ]
    )
    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert captured.err.splitlines() == [
        "error: multiple artifacts for run_id: run-b type: review_report",
        ".orchestrator_logs/run-b/review_report.json",
        ".orchestrator_logs/run-b/review_report_copy.json",
    ]


def test_missing_index_file(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "missing.json"

    rc = cli.run(["list-runs", "--index", str(missing_path)])
    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "index file not found" in captured.err


def test_invalid_index_json(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "bad.json"
    index_path.write_text("{", encoding="utf-8")

    rc = cli.run(["list-runs", "--index", str(index_path)])
    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "invalid JSON" in captured.err


def test_unknown_run_id(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(["list-artifacts", "--index", str(index_path), "--run-id", "missing"])
    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "unknown run_id" in captured.err


def test_no_artifacts_for_run(tmp_path: Path, capsys) -> None:
    index_path = tmp_path / "evidence_index.json"
    write_index(index_path, sample_index())

    rc = cli.run(["list-artifacts", "--index", str(index_path), "--run-id", "run-empty"])
    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "no artifacts" in captured.err
