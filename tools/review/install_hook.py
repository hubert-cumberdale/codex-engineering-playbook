#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
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


def read_template(template_path: Path) -> str:
    content = template_path.read_text(encoding="utf-8")
    if INSTALL_MARKER not in content:
        lines = content.splitlines()
        if lines and lines[0].startswith("#!"):
            lines.insert(1, INSTALL_MARKER)
            content = "\n".join(lines) + "\n"
        else:
            content = f"{INSTALL_MARKER}\n{content}"
    return content


def install_hook(repo_root: Path) -> Path:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / HOOK_FILENAME
    backup_path = hooks_dir / f"{HOOK_FILENAME}{BACKUP_SUFFIX}"

    template_path = Path(__file__).resolve().parent / "hooks" / HOOK_FILENAME
    template_content = read_template(template_path)

    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8")
        if INSTALL_MARKER in existing:
            return hook_path
        if not backup_path.exists():
            shutil.copy2(hook_path, backup_path)

    hook_path.write_text(template_content, encoding="utf-8")
    hook_path.chmod(0o755)
    return hook_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install codex review pre-push hook")
    parser.parse_args(argv)

    repo_root = find_repo_root(Path.cwd())
    hook_path = install_hook(repo_root)
    print(f"installed pre-push hook: {hook_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
