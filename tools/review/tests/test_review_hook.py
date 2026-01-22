from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.review import install_hook, run_review


def write_file(path: Path, content: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_minimal_repo(root: Path) -> None:
    (root / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
    for rel_path in run_review.TIER1_FILES:
        write_file(root / rel_path)
    write_file(root / "docs/releases/RELEASE_NOTES_v1.0.0.md")
    taskpack_dir = root / "taskpacks" / "TASK-EXAMPLE"
    for filename in run_review.REQUIRED_TASKPACK_FILES:
        write_file(taskpack_dir / filename)


def test_install_hook_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_minimal_repo(tmp_path)
    monkeypatch.chdir(tmp_path)

    hook_path = install_hook.install_hook(tmp_path)
    first = hook_path.read_text(encoding="utf-8")

    hook_path = install_hook.install_hook(tmp_path)
    second = hook_path.read_text(encoding="utf-8")

    assert first == second


def run_hook(tmp_path: Path, strict: bool) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONPATH": str(Path(__file__).resolve().parents[3]),
    }
    if strict:
        env["CODEX_REVIEW_STRICT"] = "1"
    return subprocess.run(
        [str(tmp_path / ".git" / "hooks" / "pre-push")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def test_hook_advisory_allows_push(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_minimal_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    install_hook.install_hook(tmp_path)

    (tmp_path / "docs/EXEC_SUMMARY.md").unlink()

    result = run_hook(tmp_path, strict=False)
    assert result.returncode == 0
    assert "advisory" in result.stdout.lower() or "advisory" in result.stderr.lower()


def test_hook_strict_blocks_on_violation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_minimal_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    install_hook.install_hook(tmp_path)

    (tmp_path / "docs/EXEC_SUMMARY.md").unlink()

    result = run_hook(tmp_path, strict=True)
    assert result.returncode == 2
