from __future__ import annotations

import json
import os
from typing import Any, Dict

from .interface import ExecutionContext
from .loader import load_plugin


def _constraint_allows(ctx: ExecutionContext, key: str) -> bool:
    # Constraints may be nested; keep it simple for v2 thin slice
    val = ctx.constraints.get(key)
    return bool(val) if val is not None else False


def run_plugin(taskpack: Dict[str, Any], ctx: ExecutionContext) -> Dict[str, Any]:
    plugin = load_plugin(taskpack)
    caps = plugin.capabilities()

    allow_network = _constraint_allows(ctx, "allow_network")
    allow_cloud_mutations = _constraint_allows(ctx, "allow_cloud_mutations")

    if caps.requires_network and not allow_network:
        raise RuntimeError(f"Plugin '{plugin.id()}' requires network, but taskpack constraints disallow it.")
    if caps.requires_cloud_mutations and not allow_cloud_mutations:
        raise RuntimeError(f"Plugin '{plugin.id()}' requires cloud mutations, but constraints disallow it.")

    # Ensure artifact dir exists
    os.makedirs(ctx.artifact_dir, exist_ok=True)

    validation = plugin.validate(taskpack, ctx)
    if not validation.ok:
        # Write result artifact even on failure
        result = {
            "plugin": {"id": plugin.id(), "version": plugin.version()},
            "validation": {"ok": False, "errors": validation.errors, "warnings": validation.warnings},
            "status": "VALIDATION_FAILED",
        }
        _write_plugin_result(ctx, result)
        return result

    plan = plugin.plan(taskpack, ctx)
    raw = plugin.run(plan, ctx)
    report_artifacts = plugin.report(raw, ctx)

    raw_artifacts = [_rel(ctx, a) for a in raw.artifacts]
    report_artifacts = [_rel(ctx, a) for a in report_artifacts]

    result = {
        "plugin": {"id": plugin.id(), "version": plugin.version()},
        "validation": {"ok": True, "errors": [], "warnings": validation.warnings},
        "plan": {"metadata": plan.metadata, "expected_artifacts": plan.expected_artifacts, "steps_count": len(plan.steps)},
        "raw": {"metadata": raw.metadata, "artifacts": raw_artifacts},
        "report_artifacts": report_artifacts,
        "status": "OK",
    }

    _write_plugin_result(ctx, result)
    return result

def _rel(ctx: ExecutionContext, p: str) -> str:
    # keep it simple and resilient across OS
    try:
        base = os.path.abspath(ctx.artifact_dir)
        ap = os.path.abspath(p)
        if ap.startswith(base + os.sep):
            return os.path.relpath(ap, base)
    except Exception:
        pass
    return p

def _write_plugin_result(ctx: ExecutionContext, result: Dict[str, Any]) -> None:
    path = os.path.join(ctx.artifact_dir, "plugin_result.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
