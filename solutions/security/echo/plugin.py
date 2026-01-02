from __future__ import annotations

import os
from typing import Any, Dict, List

from tools.orchestrator.plugins.interface import (
    ExecutionContext,
    Plan,
    PluginCapabilities,
    RawOutput,
    ValidationReport,
)


class EchoPlugin:
    def id(self) -> str:
        return "security/echo"

    def version(self) -> str:
        return "0.1.0"

    def capabilities(self) -> PluginCapabilities:
        return PluginCapabilities(
            requires_network=False,
            requires_cloud_mutations=False,
            produces_domain_result=False,
        )

    def validate(self, taskpack: Dict[str, Any], ctx: ExecutionContext) -> ValidationReport:
        return ValidationReport(ok=True)

    def plan(self, taskpack: Dict[str, Any], ctx: ExecutionContext) -> Plan:
        return Plan(
            steps=[{"action": "write_file", "path": "echo.txt", "content": "hello"}],
            expected_artifacts=["echo.txt", "echo_report.md", "plugin_result.json"],
            metadata={"note": "echo plugin plan"},
        )

    def run(self, plan: Plan, ctx: ExecutionContext) -> RawOutput:
        written: List[str] = []
        for step in plan.steps:
            if step.get("action") == "write_file":
                rel_path = step["path"]
                content = step.get("content", "")
                out_path = os.path.join(ctx.artifact_dir, rel_path)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                written.append(out_path)
            else:
                raise RuntimeError(f"Unknown step action: {step.get('action')}")
        return RawOutput(artifacts=written, metadata={"steps_ran": len(plan.steps)})

    def report(self, raw: RawOutput, ctx: ExecutionContext) -> List[str]:
        report_path = os.path.join(ctx.artifact_dir, "echo_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Echo Plugin Report\n\n")
            f.write(f"Run ID: `{ctx.run_id}`\n\n")
            f.write("## Artifacts\n")
            for a in raw.artifacts:
                f.write(f"- {os.path.basename(a)}\n")
        return [report_path]
