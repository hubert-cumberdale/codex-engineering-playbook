#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[2]


def fail(msg: str) -> None:
    print(f"[taskpack-validator] ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_yaml(path: pathlib.Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        fail(f"Failed to parse YAML: {path} ({e})")
        return {}


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate_taskpack.py <taskpack_path>")

    tp = pathlib.Path(sys.argv[1]).resolve()
    schema = load_yaml(ROOT / "taskpacks" / "schema.yml")

    for fname in schema.get("required_files", []):
        p = tp / fname
        if not p.exists():
            fail(f"Missing required file: {p}")

    task = load_yaml(tp / "task.yml")

    for k in schema.get("task_yml_required_keys", []):
        if k not in task:
            fail(f"task.yml missing required key: {k}")

    constraints = task.get("constraints", {})
    for k in schema.get("constraints_required_keys", []):
        if k not in constraints:
            fail(f"task.yml.constraints missing required key: {k}")

    acceptance = task.get("acceptance", {})
    for k in schema.get("acceptance_required_keys", []):
        if k not in acceptance:
            fail(f"task.yml.acceptance missing required key: {k}")

    # acceptance.yml must include pytest commands unless explicitly overridden
    acc_file = load_yaml(tp / "acceptance.yml")
    tests = (acc_file.get("tests") or {}).get("commands") or []
    if not any("pytest" in c for c in tests):
        fail("acceptance.yml.tests.commands must include pytest (python -m pytest ...).")

    print("[taskpack-validator] OK")


if __name__ == "__main__":
    main()
