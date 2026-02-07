from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class WorkspaceRegistryError(ValueError):
    pass


@dataclasses.dataclass(frozen=True)
class WorkspaceConfig:
    name: Optional[str]
    root: Path
    kind: str
    evidence_mode: str
    evidence_dir: Optional[Path]
    acceptance: List[str]


def evidence_paths(workspace: WorkspaceConfig, *, run_id: str) -> tuple[Path, Path]:
    if workspace.evidence_mode == "in_repo":
        evidence_root = workspace.root / ".orchestrator_logs"
    else:
        evidence_root = workspace.evidence_dir
    if evidence_root is None:
        raise WorkspaceRegistryError("Evidence directory required for external_dir mode.")
    evidence_root = evidence_root.resolve()
    return evidence_root, evidence_root / run_id


def _fail(msg: str) -> None:
    raise WorkspaceRegistryError(msg)


def _require_dict(value: Any, *, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be a mapping")
    return value


def _require_str(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string")
    return value


def _require_list_of_strings(value: Any, *, label: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        _fail(f"{label} must be a list of strings")
    return value


def load_workspace_registry(path: Path) -> Dict[str, Any]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise WorkspaceRegistryError(f"Failed to parse registry: {path} ({exc})") from exc

    data = _require_dict(raw, label="registry")

    version = data.get("version")
    if not isinstance(version, int):
        _fail("registry.version must be an integer")

    defaults = _require_dict(data.get("defaults", {}), label="registry.defaults")
    defaults_kind = _require_str(defaults.get("kind"), label="registry.defaults.kind")
    defaults_mode = _require_str(defaults.get("evidence_mode"), label="registry.defaults.evidence_mode")
    if defaults_mode not in ("in_repo", "external_dir"):
        _fail("registry.defaults.evidence_mode must be in_repo or external_dir")
    defaults_acceptance = _require_list_of_strings(
        defaults.get("acceptance"), label="registry.defaults.acceptance"
    )

    workspaces = _require_dict(data.get("workspaces", {}), label="registry.workspaces")
    for name, entry in workspaces.items():
        if not isinstance(name, str) or not name.strip():
            _fail("workspace names must be non-empty strings")
        entry = _require_dict(entry, label=f"workspace.{name}")
        kind = entry.get("kind", defaults_kind)
        if kind != "local_path":
            _fail(f"workspace.{name}.kind must be local_path")
        path_value = entry.get("path")
        _require_str(path_value, label=f"workspace.{name}.path")
        path = Path(path_value)
        if not path.is_absolute():
            _fail(f"workspace.{name}.path must be absolute")

        evidence_mode = entry.get("evidence_mode", defaults_mode)
        if evidence_mode not in ("in_repo", "external_dir"):
            _fail(f"workspace.{name}.evidence_mode must be in_repo or external_dir")
        evidence_dir = entry.get("evidence_dir")
        if evidence_mode == "external_dir":
            _require_str(evidence_dir, label=f"workspace.{name}.evidence_dir")
            if not Path(evidence_dir).is_absolute():
                _fail(f"workspace.{name}.evidence_dir must be absolute")

        _require_list_of_strings(entry.get("acceptance", defaults_acceptance), label=f"workspace.{name}.acceptance")

    return data


def resolve_workspace(
    *,
    spec: Optional[str],
    registry_path: Path,
    default_root: Path,
) -> WorkspaceConfig:
    registry = None
    if registry_path.exists():
        registry = load_workspace_registry(registry_path)

    defaults = {}
    if registry:
        defaults = registry.get("defaults", {}) or {}

    if not spec:
        _fail(
            "No workspace specified. Provide --workspace <name|path> or "
            "workspace: in task.yml (or workspace: playbook for self)."
        )

    if spec in ("playbook", "self"):
        return WorkspaceConfig(
            name=spec,
            root=default_root,
            kind="local_path",
            evidence_mode=str(defaults.get("evidence_mode", "in_repo")),
            evidence_dir=None,
            acceptance=list(defaults.get("acceptance", []) or []),
        )

    if registry:
        workspaces = registry.get("workspaces", {}) or {}
        if spec in workspaces:
            entry = workspaces[spec] or {}
            root = Path(str(entry.get("path"))).expanduser().resolve()
            if not root.exists():
                _fail(f"workspace.{spec}.path does not exist: {root}")
            evidence_mode = str(entry.get("evidence_mode", defaults.get("evidence_mode", "in_repo")))
            evidence_dir = entry.get("evidence_dir")
            evidence_dir_path = (
                Path(str(evidence_dir)).expanduser().resolve() if evidence_dir else None
            )
            if evidence_mode == "external_dir" and not evidence_dir_path:
                _fail(f"workspace.{spec}.evidence_dir required for external_dir mode")
            acceptance = entry.get("acceptance", defaults.get("acceptance", [])) or []
            return WorkspaceConfig(
                name=spec,
                root=root,
                kind=str(entry.get("kind", defaults.get("kind", "local_path"))),
                evidence_mode=evidence_mode,
                evidence_dir=evidence_dir_path,
                acceptance=list(acceptance),
            )

    # Interpret as path
    root = Path(spec).expanduser().resolve()
    if not root.exists():
        _fail(f"workspace path does not exist: {root}")
    evidence_mode = str(defaults.get("evidence_mode", "in_repo"))
    evidence_dir = defaults.get("evidence_dir")
    evidence_dir_path = Path(str(evidence_dir)).expanduser().resolve() if evidence_dir else None
    if evidence_mode == "external_dir" and not evidence_dir_path:
        _fail("workspace default evidence_dir required for external_dir mode")

    return WorkspaceConfig(
        name=None,
        root=root,
        kind=str(defaults.get("kind", "local_path")),
        evidence_mode=evidence_mode,
        evidence_dir=evidence_dir_path,
        acceptance=list(defaults.get("acceptance", []) or []),
    )
