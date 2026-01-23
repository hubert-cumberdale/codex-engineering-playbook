from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Iterable

from . import schemas


def rfc3339_utc_now() -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return timestamp.replace("+00:00", "Z")


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside repo root: {path}") from exc
    return rel.as_posix()


def _load_json(path: Path) -> dict[str, object] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _extract_schema_version(path: Path) -> int | None:
    data = _load_json(path)
    if not isinstance(data, dict):
        return None
    value = data.get("schema_version")
    if isinstance(value, int):
        return value
    return None


def _artifact_entry(
    artifact_type: str,
    path: Path,
    *,
    repo_root: Path,
    schema_version: int | None,
) -> dict[str, object]:
    return {
        "type": artifact_type,
        "path": _repo_relative(path, repo_root),
        "schema_version": schema_version,
    }


def _collect_artifacts(run_dir: Path, *, repo_root: Path) -> list[dict[str, object]]:
    artifacts: list[dict[str, object]] = []
    manifest_path = run_dir / schemas.MANIFEST_FILENAME
    if manifest_path.is_file():
        artifacts.append(
            _artifact_entry(
                "manifest",
                manifest_path,
                repo_root=repo_root,
                schema_version=None,
            )
        )

    review_path = run_dir / schemas.REVIEW_REPORT_FILENAME
    if review_path.is_file():
        artifacts.append(
            _artifact_entry(
                "review_report",
                review_path,
                repo_root=repo_root,
                schema_version=_extract_schema_version(review_path),
            )
        )

    # Deterministic behavior: ignore all other files, including evidence_index.json.
    return sorted(artifacts, key=lambda a: (a["type"], a["path"]))


def _discover_run_dirs(root: Path) -> list[Path]:
    # Run rule: any directory under the root (including the root itself) that
    # directly contains a manifest.json file is treated as a run directory.
    if not root.is_dir():
        return []

    run_dirs: dict[str, Path] = {}
    for manifest_path in sorted(root.rglob(schemas.MANIFEST_FILENAME)):
        if manifest_path.name != schemas.MANIFEST_FILENAME:
            continue
        run_dir = manifest_path.parent
        run_dirs[run_dir.resolve().as_posix()] = run_dir

    return [run_dirs[key] for key in sorted(run_dirs.keys())]


def _run_id_for(run_dir: Path, *, repo_root: Path) -> str:
    manifest_path = run_dir / schemas.MANIFEST_FILENAME
    if manifest_path.is_file():
        data = _load_json(manifest_path)
        if isinstance(data, dict):
            value = data.get("run_id")
            if isinstance(value, str) and value.strip():
                return value
    return _repo_relative(run_dir, repo_root)


def build_index(roots: Iterable[Path], *, repo_root: Path) -> dict[str, object]:
    root_paths = [root for root in roots]
    roots_scanned: list[str] = []
    for root in root_paths:
        root_rel = _repo_relative(root, repo_root)
        if root_rel not in roots_scanned:
            roots_scanned.append(root_rel)

    runs: list[dict[str, object]] = []
    seen_run_dirs: set[str] = set()
    for root in root_paths:
        for run_dir in _discover_run_dirs(root):
            run_rel = _repo_relative(run_dir, repo_root)
            if run_rel in seen_run_dirs:
                continue
            seen_run_dirs.add(run_rel)

            manifest_path = run_dir / schemas.MANIFEST_FILENAME
            manifest_rel = _repo_relative(manifest_path, repo_root) if manifest_path.is_file() else None
            run_entry = {
                "run_id": _run_id_for(run_dir, repo_root=repo_root),
                "run_dir": run_rel,
                "manifest_path": manifest_rel,
                "artifacts": _collect_artifacts(run_dir, repo_root=repo_root),
            }
            runs.append(run_entry)

    runs.sort(key=lambda r: (r["run_id"], r["run_dir"]))

    return {
        "schema_version": schemas.INDEX_SCHEMA_VERSION,
        "generated_at": rfc3339_utc_now(),
        "roots_scanned": roots_scanned,
        "runs": runs,
    }


def serialize_index(index: dict[str, object]) -> str:
    return json.dumps(index, indent=2, sort_keys=True) + "\n"


def write_index(index: dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(serialize_index(index), encoding="utf-8")
