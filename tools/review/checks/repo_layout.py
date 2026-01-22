from __future__ import annotations

from pathlib import Path

TIER1_DOCS = (
    "docs/EXEC_SUMMARY.md",
    "docs/VERSIONING.md",
    "docs/GOVERNANCE.md",
    "docs/Canonical Conventions.md",
    "docs/System Overview.md",
)


def check(repo_root: Path) -> list[str]:
    violations: list[str] = []

    for doc_path in TIER1_DOCS:
        if not (repo_root / doc_path).is_file():
            violations.append(f"Missing required doc: {doc_path}")

    if not (repo_root / ".codex" / "library").is_dir():
        violations.append("Missing prompt library directory: .codex/library")

    return violations
