from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol


@dataclass(frozen=True)
class PluginCapabilities:
    requires_network: bool = False
    requires_cloud_mutations: bool = False
    produces_domain_result: bool = True


@dataclass(frozen=True)
class ExecutionContext:
    run_id: str
    taskpack_path: str
    workspace_dir: str
    constraints: Dict[str, Any]
    artifact_dir: str
    log: Callable[..., None] = print


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Plan:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    expected_artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RawOutput:
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SolutionPlugin(Protocol):
    def id(self) -> str: ...
    def version(self) -> str: ...
    def capabilities(self) -> PluginCapabilities: ...
    def validate(self, taskpack: Dict[str, Any], ctx: ExecutionContext) -> ValidationReport: ...
    def plan(self, taskpack: Dict[str, Any], ctx: ExecutionContext) -> Plan: ...
    def run(self, plan: Plan, ctx: ExecutionContext) -> RawOutput: ...
    def report(self, raw: RawOutput, ctx: ExecutionContext) -> List[str]: ...
