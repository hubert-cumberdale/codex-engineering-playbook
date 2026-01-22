#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

HOOK_FILENAME = "pre-push"
BACKUP_SUFFIX = ".codex.bak"
INSTALL_MARKER = "# codex-review-hook"


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(".git directory not found")


def uninstall_hook(repo_root: Path) -> Path | None:
    hooks_dir = repo_root / ".git" / "hooks"
    hook_path = hooks_dir / HOOK_FILENAME
    backup_path = hooks_dir / f"{HOOK_FILENAME}{BACKUP_SUFFIX}"

    if not hook_path.exists():
        return None

    existing = hook_path.read_text(encoding="utf-8")
    if INSTALL_MARKER not in existing:
        return None

    if backup_path.exists():
        hook_path.unlink()
        backup_path.replace(hook_path)
        return hook_path

    hook_path.unlink()
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Uninstall codex review pre-push hook")
    parser.parse_args(argv)

    repo_root = find_repo_root(Path.cwd())
    restored = uninstall_hook(repo_root)
    if restored is None:
        print("no codex review hook installed")
    else:
        print(f"restored previous hook: {restored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
