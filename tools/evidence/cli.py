from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import index as evidence_index


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="tools.evidence.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Build evidence index JSON")
    index_parser.add_argument(
        "--root",
        action="append",
        default=None,
        help="Root directory to scan (default: .orchestrator_logs). Can be repeated.",
    )
    index_parser.add_argument(
        "--out",
        default=".orchestrator_logs/evidence_index.json",
        help="Output JSON path (default: .orchestrator_logs/evidence_index.json).",
    )

    list_runs_parser = subparsers.add_parser("list-runs", help="List runs from index")
    list_runs_parser.add_argument(
        "--index",
        default=".orchestrator_logs/evidence_index.json",
        help="Evidence index JSON path (default: .orchestrator_logs/evidence_index.json).",
    )

    list_artifacts_parser = subparsers.add_parser(
        "list-artifacts",
        help="List artifacts for a run from index",
    )
    list_artifacts_parser.add_argument(
        "--index",
        default=".orchestrator_logs/evidence_index.json",
        help="Evidence index JSON path (default: .orchestrator_logs/evidence_index.json).",
    )
    list_artifacts_parser.add_argument("--run-id", required=True, help="Run id to query.")

    show_artifact_parser = subparsers.add_parser(
        "show-artifact",
        help="Show a single artifact path for a run and type",
    )
    show_artifact_parser.add_argument(
        "--index",
        default=".orchestrator_logs/evidence_index.json",
        help="Evidence index JSON path (default: .orchestrator_logs/evidence_index.json).",
    )
    show_artifact_parser.add_argument("--run-id", required=True, help="Run id to query.")
    show_artifact_parser.add_argument("--type", dest="artifact_type", required=True, help="Artifact type.")

    meta_parser = subparsers.add_parser("show-index-meta", help="Show index metadata")
    meta_parser.add_argument(
        "--index",
        default=".orchestrator_logs/evidence_index.json",
        help="Evidence index JSON path (default: .orchestrator_logs/evidence_index.json).",
    )

    return parser.parse_args(argv)


def _normalize_roots(root_args: list[str] | None, *, repo_root: Path) -> list[Path]:
    roots = root_args if root_args else [".orchestrator_logs"]
    paths: list[Path] = []
    for root in roots:
        root_path = Path(root)
        if not root_path.is_absolute():
            root_path = repo_root / root_path
        paths.append(root_path.resolve())
    return paths


def _load_index(index_path: Path) -> dict[str, object]:
    if not index_path.exists():
        raise ValueError(f"index file not found: {index_path}")
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in index file: {index_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("invalid index schema: top-level JSON must be an object")
    if "runs" not in data:
        raise ValueError("invalid index schema: missing runs")
    if not isinstance(data["runs"], list):
        raise ValueError("invalid index schema: runs must be a list")
    return data


def _find_run(index: dict[str, object], run_id: str) -> dict[str, object] | None:
    runs = index.get("runs")
    if not isinstance(runs, list):
        return None
    for run in runs:
        if isinstance(run, dict) and run.get("run_id") == run_id:
            return run
    return None


def _format_schema_version(value: object) -> str:
    if isinstance(value, int):
        return str(value)
    return "-"


def _emit_list_runs(index: dict[str, object]) -> None:
    runs = index.get("runs", [])
    if not isinstance(runs, list):
        raise ValueError("invalid index schema: runs must be a list")
    sorted_runs = sorted(
        (run for run in runs if isinstance(run, dict)),
        key=lambda r: (str(r.get("run_id", "")), str(r.get("run_dir", ""))),
    )
    for run in sorted_runs:
        run_id = str(run.get("run_id", ""))
        run_dir = str(run.get("run_dir", ""))
        print(f"{run_id}\t{run_dir}")


def _emit_list_artifacts(index: dict[str, object], run_id: str) -> None:
    run = _find_run(index, run_id)
    if run is None:
        raise ValueError(f"unknown run_id: {run_id}")
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"no artifacts for run_id: {run_id}")
    sorted_artifacts = sorted(
        (a for a in artifacts if isinstance(a, dict)),
        key=lambda a: (str(a.get("type", "")), str(a.get("path", ""))),
    )
    for artifact in sorted_artifacts:
        artifact_type = str(artifact.get("type", ""))
        path = str(artifact.get("path", ""))
        schema_version = _format_schema_version(artifact.get("schema_version"))
        print(f"{artifact_type}\t{path}\t{schema_version}")


def _emit_show_artifact(index: dict[str, object], run_id: str, artifact_type: str) -> None:
    run = _find_run(index, run_id)
    if run is None:
        raise ValueError(f"unknown run_id: {run_id}")
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"no artifacts for run_id: {run_id}")
    matches = [
        artifact
        for artifact in artifacts
        if isinstance(artifact, dict) and artifact.get("type") == artifact_type
    ]
    if not matches:
        raise ValueError(f"no artifacts for run_id: {run_id} type: {artifact_type}")
    if len(matches) > 1:
        paths = sorted(str(match.get("path", "")) for match in matches)
        message = f"multiple artifacts for run_id: {run_id} type: {artifact_type}"
        raise ValueError(message + "\n" + "\n".join(paths))
    print(str(matches[0].get("path", "")))


def _emit_show_meta(index: dict[str, object]) -> None:
    schema_version = index.get("schema_version")
    generated_at = index.get("generated_at")
    roots_scanned = index.get("roots_scanned")
    runs = index.get("runs", [])
    roots_value = ""
    if isinstance(roots_scanned, list):
        roots_value = ",".join(str(root) for root in roots_scanned)
    print(f"schema_version\t{schema_version}")
    print(f"generated_at\t{generated_at}")
    print(f"roots_scanned\t{roots_value}")
    print(f"run_count\t{len(runs) if isinstance(runs, list) else 0}")


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = Path.cwd().resolve()

    if args.command == "index":
        roots = _normalize_roots(args.root, repo_root=repo_root)
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = (repo_root / out_path).resolve()
        try:
            index = evidence_index.build_index(roots, repo_root=repo_root)
            evidence_index.write_index(index, out_path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0
    if args.command in {
        "list-runs",
        "list-artifacts",
        "show-artifact",
        "show-index-meta",
    }:
        index_path = Path(args.index)
        if not index_path.is_absolute():
            index_path = (repo_root / index_path).resolve()
        try:
            index = _load_index(index_path)
            if args.command == "list-runs":
                _emit_list_runs(index)
            elif args.command == "list-artifacts":
                _emit_list_artifacts(index, args.run_id)
            elif args.command == "show-artifact":
                _emit_show_artifact(index, args.run_id, args.artifact_type)
            elif args.command == "show-index-meta":
                _emit_show_meta(index)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    print(f"error: unknown command {args.command}", file=sys.stderr)
    return 1


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
