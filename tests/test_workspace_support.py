from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.orchestrator.orchestrate import (
    TaskPack,
    ensure_required_docs,
    enforce_scope_allowed_paths,
    select_workspace_spec,
)
from tools.orchestrator.workspaces import (
    WorkspaceRegistryError,
    evidence_paths,
    load_workspace_registry,
    resolve_workspace,
)


def _write_registry(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)


def _commit_all(path: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=path, check=True)


def test_workspace_registry_loads_valid(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        """
version: 1
defaults:
  kind: local_path
  evidence_mode: in_repo
  acceptance:
    - python -m pytest -q
workspaces:
  alpha:
    kind: local_path
    path: /tmp/alpha
    evidence_mode: in_repo
""",
    )
    data = load_workspace_registry(registry_path)
    assert data["version"] == 1
    assert "workspaces" in data


def test_workspace_registry_rejects_missing_evidence_dir(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        """
version: 1
defaults:
  kind: local_path
  evidence_mode: external_dir
workspaces:
  alpha:
    kind: local_path
    path: /tmp/alpha
    evidence_mode: external_dir
""",
    )
    with pytest.raises(WorkspaceRegistryError):
        load_workspace_registry(registry_path)


def test_workspace_resolution_name_vs_path(tmp_path: Path) -> None:
    workspace_root = tmp_path / "repo"
    workspace_root.mkdir()
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        f"""
version: 1
defaults:
  kind: local_path
  evidence_mode: in_repo
workspaces:
  alpha:
    kind: local_path
    path: {workspace_root.as_posix()}
    evidence_mode: in_repo
""",
    )
    resolved = resolve_workspace(spec="alpha", registry_path=registry_path, default_root=tmp_path)
    assert resolved.root == workspace_root.resolve()

    other_root = tmp_path / "other"
    other_root.mkdir()
    resolved_path = resolve_workspace(
        spec=str(other_root),
        registry_path=registry_path,
        default_root=tmp_path,
    )
    assert resolved_path.root == other_root.resolve()


def test_workspace_spec_precedence() -> None:
    assert (
        select_workspace_spec(
            cli_value="cli",
            env_value="env",
            task_value="task",
        )
        == "cli"
    )
    assert (
        select_workspace_spec(
            cli_value=None,
            env_value="env",
            task_value="task",
        )
        == "env"
    )
    assert (
        select_workspace_spec(
            cli_value=None,
            env_value=None,
            task_value="task",
        )
        == "task"
    )


def test_missing_workspace_is_error(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        """
version: 1
defaults:
  kind: local_path
  evidence_mode: in_repo
workspaces: {}
""",
    )
    with pytest.raises(WorkspaceRegistryError) as excinfo:
        resolve_workspace(spec=None, registry_path=registry_path, default_root=tmp_path)
    assert str(excinfo.value) == (
        "No workspace specified. Provide --workspace <name|path> or "
        "workspace: in task.yml (or workspace: playbook for self)."
    )


def test_playbook_alias_targets_default_root(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        """
version: 1
defaults:
  kind: local_path
  evidence_mode: in_repo
workspaces: {}
""",
    )
    resolved = resolve_workspace(spec="playbook", registry_path=registry_path, default_root=tmp_path)
    assert resolved.root == tmp_path.resolve()


def test_evidence_paths_routing(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    registry_path = tmp_path / "registry.yml"
    _write_registry(
        registry_path,
        f"""
version: 1
defaults:
  kind: local_path
  evidence_mode: in_repo
workspaces:
  alpha:
    kind: local_path
    path: {repo_root.as_posix()}
    evidence_mode: in_repo
  beta:
    kind: local_path
    path: {repo_root.as_posix()}
    evidence_mode: external_dir
    evidence_dir: {tmp_path.joinpath("evidence").as_posix()}
""",
    )
    in_repo = resolve_workspace(spec="alpha", registry_path=registry_path, default_root=tmp_path)
    root, run_dir = evidence_paths(in_repo, run_id="run-1")
    assert root == repo_root / ".orchestrator_logs"
    assert run_dir == repo_root / ".orchestrator_logs" / "run-1"

    external = resolve_workspace(spec="beta", registry_path=registry_path, default_root=tmp_path)
    root, run_dir = evidence_paths(external, run_id="run-2")
    assert root == tmp_path / "evidence"
    assert run_dir == tmp_path / "evidence" / "run-2"


def test_docs_required_check(tmp_path: Path) -> None:
    workspace_root = tmp_path / "repo"
    workspace_root.mkdir()
    (workspace_root / "docs").mkdir()
    (workspace_root / "docs" / "GOVERNANCE.md").write_text("ok", encoding="utf-8")

    tp = TaskPack(
        path=tmp_path,
        task={"docs": {"required": ["docs/GOVERNANCE.md", "docs/CURRENT_WORK.md"]}},
        spec="",
        risk="",
        acceptance={},
    )

    with pytest.raises(SystemExit):
        ensure_required_docs(tp, workspace_root=workspace_root)

    (workspace_root / "docs" / "CURRENT_WORK.md").write_text("ok", encoding="utf-8")
    ensure_required_docs(tp, workspace_root=workspace_root)


def test_scope_allowed_paths_enforced(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    (repo / "README.md").write_text("base", encoding="utf-8")
    _commit_all(repo, "base")
    base_ref = (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
    )

    (repo / "src").mkdir()
    (repo / "src" / "ok.txt").write_text("ok", encoding="utf-8")
    _commit_all(repo, "allowed change")

    tp = TaskPack(
        path=tmp_path,
        task={"scope": {"allowed_paths": ["src/"]}},
        spec="",
        risk="",
        acceptance={},
    )
    enforce_scope_allowed_paths(tp, workspace_root=repo, base_ref=base_ref)


def test_scope_allowed_paths_violation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    (repo / "README.md").write_text("base", encoding="utf-8")
    _commit_all(repo, "base")
    base_ref = (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
    )

    (repo / "secrets").mkdir()
    (repo / "secrets" / "nope.txt").write_text("nope", encoding="utf-8")
    _commit_all(repo, "bad change")

    tp = TaskPack(
        path=tmp_path,
        task={"scope": {"allowed_paths": ["src/"]}},
        spec="",
        risk="",
        acceptance={},
    )
    with pytest.raises(SystemExit):
        enforce_scope_allowed_paths(tp, workspace_root=repo, base_ref=base_ref)
