from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.orchestrator import orchestrate


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def setup_orchestrator_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log_dir = tmp_path / ".orchestrator_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(orchestrate, "ROOT", tmp_path)
    monkeypatch.setattr(orchestrate, "LOG_DIR", log_dir)
    return log_dir


def test_evidence_index_default_disabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = setup_orchestrator_paths(tmp_path, monkeypatch)
    manifest_path = log_dir / "manifest.json"
    manifest = {"result": "started"}
    orchestrate._write_manifest(manifest_path, manifest)

    orchestrate._maybe_collect_evidence_index(False, manifest, manifest_path=manifest_path)

    assert not (log_dir / "evidence_index.json").exists()
    assert read_json(manifest_path) == {"result": "started"}


def test_evidence_index_opt_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = setup_orchestrator_paths(tmp_path, monkeypatch)
    manifest_path = log_dir / "manifest.json"
    manifest = {"result": "started"}
    orchestrate._write_manifest(manifest_path, manifest)

    orchestrate._maybe_collect_evidence_index(True, manifest, manifest_path=manifest_path)

    index_path = log_dir / "evidence_index.json"
    assert index_path.exists()
    index = read_json(index_path)
    assert index["schema_version"] == 1

    manifest_out = read_json(manifest_path)
    assert manifest_out["evidence_index_path"] == ".orchestrator_logs/evidence_index.json"
    assert manifest_out["evidence_index_schema_version"] == 1
    assert "evidence_index_error" not in manifest_out


def test_evidence_index_failure_is_non_fatal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_dir = setup_orchestrator_paths(tmp_path, monkeypatch)
    manifest_path = log_dir / "manifest.json"
    manifest = {"result": "started"}
    orchestrate._write_manifest(manifest_path, manifest)

    def _raise(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(orchestrate.evidence_index, "build_index", _raise)

    orchestrate._maybe_collect_evidence_index(True, manifest, manifest_path=manifest_path)

    assert not (log_dir / "evidence_index.json").exists()
    manifest_out = read_json(manifest_path)
    assert manifest_out.get("evidence_index_error") == "ValueError: boom"
    assert "evidence_index_path" not in manifest_out
    assert "evidence_index_schema_version" not in manifest_out
