from __future__ import annotations

from pathlib import Path

REQUIRED_FILES = (
    "task.yml",
    "spec.md",
    "acceptance.yml",
    "risk.md",
    "runbook.md",
)


def check(repo_root: Path) -> list[str]:
    violations: list[str] = []
    taskpacks_root = repo_root / "taskpacks"
    if not taskpacks_root.is_dir():
        return ["Missing taskpacks/ directory"]

    taskpack_dirs = sorted(
        entry
        for entry in taskpacks_root.iterdir()
        if entry.is_dir() and entry.name.startswith("TASK-")
    )

    for taskpack_dir in taskpack_dirs:
        for filename in REQUIRED_FILES:
            path = taskpack_dir / filename
            if not path.is_file():
                rel_path = path.relative_to(repo_root).as_posix()
                violations.append(f"Missing required taskpack file: {rel_path}")

    return violations
