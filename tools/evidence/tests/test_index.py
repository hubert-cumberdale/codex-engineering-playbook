from __future__ import annotations

import json
from pathlib import Path

from tools.evidence import index as evidence_index
from tools.evidence import schemas


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_index_deterministic_ordering(tmp_path: Path) -> None:
    repo_root = tmp_path
    logs_root = repo_root / ".orchestrator_logs"

    run_a = logs_root / "run-a"
    run_b = logs_root / "run-b"
    ignored_run = logs_root / "run-no-manifest"

    write_json(run_a / schemas.MANIFEST_FILENAME, {"run_id": "b-run"})
    write_json(run_b / schemas.MANIFEST_FILENAME, {"run_id": "a-run"})
    ignored_run.mkdir(parents=True, exist_ok=True)

    write_json(
        run_b / schemas.REVIEW_REPORT_FILENAME,
        {"schema_version": 1, "violations": []},
    )

    # Ensure self-index artifacts are ignored.
    (run_b / schemas.INDEX_FILENAME).write_text("{}", encoding="utf-8")

    index = evidence_index.build_index([logs_root], repo_root=repo_root)

    assert index["schema_version"] == schemas.INDEX_SCHEMA_VERSION
    assert index["roots_scanned"] == [".orchestrator_logs"]

    runs = index["runs"]
    assert [run["run_id"] for run in runs] == ["a-run", "b-run"]
    assert [run["run_dir"] for run in runs] == [
        ".orchestrator_logs/run-b",
        ".orchestrator_logs/run-a",
    ]
    assert all(run["run_dir"] != ".orchestrator_logs/run-no-manifest" for run in runs)

    run_b_entry = runs[0]
    assert run_b_entry["manifest_path"] == ".orchestrator_logs/run-b/manifest.json"

    artifacts = run_b_entry["artifacts"]
    assert [artifact["type"] for artifact in artifacts] == ["manifest", "review_report"]
    assert [artifact["path"] for artifact in artifacts] == [
        ".orchestrator_logs/run-b/manifest.json",
        ".orchestrator_logs/run-b/review_report.json",
    ]
    assert [artifact["schema_version"] for artifact in artifacts] == [None, 1]

    assert all(schemas.INDEX_FILENAME not in artifact["path"] for artifact in artifacts)


def test_review_report_invalid_json_schema_version_null(tmp_path: Path) -> None:
    repo_root = tmp_path
    logs_root = repo_root / ".orchestrator_logs"
    run_dir = logs_root / "run-invalid"
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / schemas.MANIFEST_FILENAME, {"run_id": "invalid-json"})
    (run_dir / schemas.REVIEW_REPORT_FILENAME).write_text("{", encoding="utf-8")

    index = evidence_index.build_index([logs_root], repo_root=repo_root)
    assert len(index["runs"]) == 1
    artifacts = index["runs"][0]["artifacts"]
    assert [artifact["type"] for artifact in artifacts] == ["manifest", "review_report"]
    assert [artifact["schema_version"] for artifact in artifacts] == [None, None]
