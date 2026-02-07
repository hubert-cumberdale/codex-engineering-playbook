#!/usr/bin/env python3
"""
Codex Orchestrator (GitHub Actions)

- Reads a Task Pack (spec + acceptance + risk + task.yml)
- Creates a branch
- Runs phased Codex CLI executions with retries:
  Planner -> Implementer -> Verifier -> Security -> PR Author
- Runs acceptance commands locally
- Commits/pushes changes and opens PR via gh

Design goals:
- Fault-tolerant: retries per phase, preserves logs, can fail fast with context
- Anti-context-rot: always derives truth from Task Pack + repo files, not chat history
"""

from __future__ import annotations
from pathlib import Path

import argparse
import dataclasses
import json
import os
import pathlib
import shlex
import subprocess
import sys
import textwrap
import time
from typing import List, Optional, Tuple

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / ".orchestrator_logs"
LOG_DIR = LOG_ROOT
LOG_ROOT.mkdir(exist_ok=True)

# Ensure repo root is on sys.path so absolute imports like `tools.*` work
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# v2 plugin thin-slice
from tools.evidence import index as evidence_index
from tools.evidence import schemas as evidence_schemas
from tools.orchestrator.plugins.runner import run_plugin
from tools.orchestrator.plugins.interface import ExecutionContext
from tools.orchestrator.workspaces import WorkspaceRegistryError, evidence_paths, resolve_workspace

@dataclasses.dataclass
class TaskPack:
    path: pathlib.Path
    task: dict
    spec: str
    risk: str
    acceptance: dict

    @property
    def id(self) -> str:
        return str(self.task.get("id", "TASK-UNKNOWN"))

    @property
    def title(self) -> str:
        return str(self.task.get("title", "Untitled"))

    @property
    def allow_network(self) -> bool:
        return bool(self.task.get("constraints", {}).get("allow_network", False))

    @property
    def allow_cloud_mutations(self) -> bool:
        return bool(self.task.get("constraints", {}).get("allow_cloud_mutations", False))

    @property
    def preferred_skills(self) -> List[str]:
        return list(self.task.get("skills", {}).get("prefer", []))


def run(cmd: str, *, cwd: pathlib.Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and proc.returncode != 0:
        # Print captured output so failures are actionable
        print(proc.stdout or "")
        raise subprocess.CalledProcessError(proc.returncode, cmd, output=proc.stdout)
    return proc

def must_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument(
        "--enable-plugins",
        action="store_true",
        help="Run v2 solution plugin specified by taskpack.task.plugin (default: disabled). "
            "Can also set ORCH_ENABLE_PLUGINS=1."
    )
    p.add_argument(
        "--plugins-strict",
        action="store_true",
        help="Fail the run if plugin execution errors (default: non-fatal, recorded in manifest). "
            "Can also set ORCH_PLUGINS_STRICT=1.",
    )
    p.add_argument(
        "--workspace",
        help="Workspace registry name or local path. Can also set ORCH_WORKSPACE.",
    )
    return p.parse_args(argv)

def _env_truthy(name: str) -> bool:
    v = os.getenv(name, "").strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def _path_for_manifest(path: pathlib.Path, *, repo_root: pathlib.Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _is_relative_to(path: pathlib.Path, base: pathlib.Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def select_workspace_spec(
    *,
    cli_value: Optional[str],
    env_value: Optional[str],
    task_value: Optional[str],
) -> Optional[str]:
    return cli_value or env_value or task_value

def _write_manifest(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")

def _collect_review_report(
    manifest: dict,
    *,
    manifest_path: pathlib.Path,
    log_dir: pathlib.Path,
    repo_root: pathlib.Path,
    cwd: pathlib.Path,
) -> None:
    report_path = log_dir / "review_report.json"
    cmd = (
        f"PYTHONPATH={shlex.quote(str(ROOT))} {shlex.quote(sys.executable)} -m tools.review.run_review "
        f"--mode advisory --report-path {shlex.quote(str(report_path))}"
    )
    proc = run(cmd, check=False, cwd=cwd)

    if proc.returncode == 0:
        status = "pass"
    elif proc.returncode == 2:
        status = "violations"
    else:
        status = "error"

    if report_path.exists():
        manifest["review_report_path"] = _path_for_manifest(report_path, repo_root=repo_root)
        manifest["review_schema_version"] = 1
        manifest["review_status"] = status
    else:
        manifest["review_status"] = "error"
        manifest["review_error"] = "review_report_missing"

    _write_manifest(manifest_path, manifest)
    print(f"[review] collected status={status} report={report_path}")


def _collect_evidence_index(
    manifest: dict,
    *,
    manifest_path: pathlib.Path,
    evidence_root: pathlib.Path,
    repo_root: pathlib.Path,
) -> None:
    index_path = evidence_root / evidence_schemas.INDEX_FILENAME
    try:
        index = evidence_index.build_index([evidence_root], repo_root=repo_root)
        evidence_index.write_index(index, index_path)
        manifest["evidence_index_path"] = _path_for_manifest(index_path, repo_root=repo_root)
        manifest["evidence_index_schema_version"] = evidence_schemas.INDEX_SCHEMA_VERSION
        manifest.pop("evidence_index_error", None)
        _write_manifest(manifest_path, manifest)
        print(f"[evidence] index written: {index_path}")
    except Exception as exc:
        manifest["evidence_index_error"] = f"{type(exc).__name__}: {exc}"
        _write_manifest(manifest_path, manifest)
        print(f"[evidence] index failed: {manifest['evidence_index_error']}")


def _maybe_collect_evidence_index(
    enabled: bool,
    manifest: dict,
    *,
    manifest_path: pathlib.Path,
    evidence_root: pathlib.Path,
    repo_root: pathlib.Path,
) -> None:
    if not enabled:
        return
    _collect_evidence_index(
        manifest,
        manifest_path=manifest_path,
        evidence_root=evidence_root,
        repo_root=repo_root,
    )

def _make_execution_context(
    tp: TaskPack,
    *,
    run_id: str,
    workspace_dir: pathlib.Path,
    artifact_dir: pathlib.Path,
    log_dir: pathlib.Path,
) -> ExecutionContext:
    artifact_dir.mkdir(parents=True, exist_ok=True)

    constraints = dict(tp.task.get("constraints", {}) or {})

    plugin_log_path = log_dir / f"plugin_{tp.id.lower()}.log"

    def _log(*args, **kwargs) -> None:
        msg = " ".join(str(a) for a in args)
        try:
            with open(plugin_log_path, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception:
            pass
        print(*args, **kwargs)

    return ExecutionContext(
        run_id=run_id,
        taskpack_path=str(tp.path),
        workspace_dir=str(workspace_dir),
        constraints=constraints,
        artifact_dir=str(artifact_dir),
        log=_log,
    )

def load_taskpack(tp_path: pathlib.Path) -> TaskPack:
    task_yml = tp_path / "task.yml"
    spec_md = tp_path / "spec.md"
    risk_md = tp_path / "risk.md"
    acc_yml = tp_path / "acceptance.yml"

    for f in (task_yml, spec_md, risk_md, acc_yml):
        if not f.exists():
            raise SystemExit(f"Task pack missing required file: {f}")

    task = yaml.safe_load(task_yml.read_text(encoding="utf-8")) or {}
    spec = spec_md.read_text(encoding="utf-8")
    risk = risk_md.read_text(encoding="utf-8")
    acceptance = yaml.safe_load(acc_yml.read_text(encoding="utf-8")) or {}

    return TaskPack(path=tp_path, task=task, spec=spec, risk=risk, acceptance=acceptance)


def ensure_required_docs(tp: TaskPack, *, workspace_root: pathlib.Path) -> None:
    required = (tp.task.get("docs", {}) or {}).get("required", []) or []
    missing = []
    for rel in required:
        path = workspace_root / rel
        if not path.exists():
            missing.append(str(path))
    if missing:
        raise SystemExit(f"Missing required docs in workspace: {', '.join(missing)}")


def ensure_managed_repo_contracts(tp: TaskPack, *, workspace_root: pathlib.Path, playbook_root: pathlib.Path) -> None:
    if workspace_root == playbook_root:
        return
    docs_required = (tp.task.get("docs", {}) or {}).get("required", []) or []
    allowed_paths = (tp.task.get("scope", {}) or {}).get("allowed_paths", []) or []
    missing = []
    if not docs_required:
        missing.append("docs.required")
    if not allowed_paths:
        missing.append("scope.allowed_paths")
    if missing:
        raise SystemExit(
            "Managed repo taskpacks must declare non-empty "
            + " and ".join(missing)
        )


def _path_within_prefix(path: str, prefix: str) -> bool:
    path_parts = pathlib.PurePosixPath(path).parts
    prefix_parts = pathlib.PurePosixPath(prefix).parts
    if not prefix_parts:
        return False
    return path_parts[: len(prefix_parts)] == prefix_parts


def enforce_scope_allowed_paths(
    tp: TaskPack,
    *,
    workspace_root: pathlib.Path,
    base_ref: str,
) -> None:
    allowed = (tp.task.get("scope", {}) or {}).get("allowed_paths", []) or []
    if not allowed:
        return
    diff = run(
        f"git diff --name-only {shlex.quote(base_ref)}...HEAD",
        cwd=workspace_root,
        check=True,
    ).stdout
    changed = [line.strip() for line in (diff or "").splitlines() if line.strip()]
    violations = [p for p in changed if not any(_path_within_prefix(p, a) for a in allowed)]
    if violations:
        raise SystemExit(
            "Changes outside scope.allowed_paths: "
            + ", ".join(sorted(violations))
        )


def git_current_branch(*, cwd: pathlib.Path) -> str:
    return run("git rev-parse --abbrev-ref HEAD", cwd=cwd).stdout.strip()


def git_has_changes(*, cwd: pathlib.Path) -> bool:
    out = run("git status --porcelain", check=False, cwd=cwd).stdout.strip()
    return bool(out)


def git_commit(message: str, *, cwd: pathlib.Path) -> None:
    run("git add -A", cwd=cwd)
    if not git_has_changes(cwd=cwd):
        return
    run(f"git commit -m {shlex.quote(message)}", cwd=cwd)


def gh_pr_create(
    title: str,
    body: str,
    *,
    base: str = "main",
    cwd: pathlib.Path,
    log_dir: pathlib.Path,
) -> str:
    # GitHub Actions usually has GH_TOKEN set automatically.
    # We'll rely on `gh` being present on runner (it is on ubuntu-latest).
    body_file = log_dir / "pr_body.md"
    body_file.write_text(body, encoding="utf-8")
    cmd = f"gh pr create --base {shlex.quote(base)} --title {shlex.quote(title)} --body-file {shlex.quote(str(body_file))}"
    out = run(cmd, cwd=cwd).stdout.strip().splitlines()[-1]
    return out

def default_pr_body(tp: TaskPack, *, branch_name: str, base_branch: str) -> str:
    return textwrap.dedent(
        f"""
        ## Evidence
        - Evidence root: {{evidence_root}}
        - Run ID: {{run_id}}

        ### Acceptance results
        {{acceptance_results}}

        ## Files changed
        {{files_changed}}

        ## Contract docs referenced
        {{contract_docs}}

        ## Summary
        - Task Pack: {tp.id} ({tp.title})
        - Branch: {branch_name} → {base_branch}
        """
    ).strip()


def _format_acceptance_results(results: list[dict[str, str]]) -> str:
    if not results:
        return "- No acceptance commands executed."
    lines = []
    for result in results:
        status = result.get("status", "unknown")
        section = result.get("section", "unknown")
        command = result.get("command", "")
        log_path = result.get("log_path", "")
        detail = f" (log: {log_path})" if log_path else ""
        lines.append(f"- [{status}] {section}: `{command}`{detail}")
    return "\n".join(lines)


def _format_contract_docs(docs: list[str]) -> str:
    if not docs:
        return "- None."
    return "\n".join(f"- {doc}" for doc in docs)


def _format_files_changed(*, workspace_root: pathlib.Path, base_ref: str) -> str:
    proc = run(
        f"git diff --stat {shlex.quote(base_ref)}...HEAD",
        cwd=workspace_root,
        check=False,
    )
    summary = (proc.stdout or "").strip()
    if not summary:
        return "No changes."
    return summary


def build_pr_body(
    tp: TaskPack,
    *,
    branch_name: str,
    base_branch: str,
    evidence_root: pathlib.Path,
    run_id: str,
    acceptance_results: list[dict[str, str]],
    workspace_root: pathlib.Path,
    extra_body: str | None = None,
) -> str:
    template = default_pr_body(tp, branch_name=branch_name, base_branch=base_branch)
    base = (
        template.replace("{evidence_root}", str(evidence_root))
        .replace("{run_id}", run_id)
        .replace("{acceptance_results}", _format_acceptance_results(acceptance_results))
        .replace("{files_changed}", _format_files_changed(workspace_root=workspace_root, base_ref=base_branch))
        .replace("{contract_docs}", _format_contract_docs((tp.task.get("docs", {}) or {}).get("required", [])))
    )
    if extra_body:
        return f"{base}\n\n## Notes\n{extra_body.strip()}"
    return base

def codex_exec(
    prompt: str,
    *,
    log_name: str,
    cwd: pathlib.Path,
    log_dir: pathlib.Path,
) -> Tuple[int, str]:
    """
    Runs Codex in non-interactive mode.
    We use `codex exec` so the agent can modify files and run commands as needed,
    but we keep our own acceptance commands outside of Codex as a safety/ground-truth step.
    """
    log_path = log_dir / f"{log_name}.log"
    # Use --json if you want structured output later; for now keep plain logs.
    cmd = f"codex exec {shlex.quote(prompt)}"
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path.write_text(proc.stdout or "", encoding="utf-8")
    return proc.returncode, proc.stdout or ""


def render_common_context(tp: TaskPack) -> str:
    skills = ", ".join(tp.preferred_skills) if tp.preferred_skills else "(none specified)"
    return textwrap.dedent(
        f"""
        TaskPack:
        - id: {tp.id}
        - title: {tp.title}
        - path: {tp.path.as_posix()}
        - allow_network: {tp.allow_network}
        - allow_cloud_mutations: {tp.allow_cloud_mutations}
        - preferred_skills: {skills}

        Spec:
        {tp.spec}

        Risk Notes:
        {tp.risk}

        Acceptance:
        {yaml.safe_dump(tp.acceptance, sort_keys=False)}
        """
    ).strip()


def phase_prompt(tp: TaskPack, phase: str) -> str:
    ctx = render_common_context(tp)

    # Minimal “agent role” shaping without relying on long conversation history.
    if phase == "planner":
        return textwrap.dedent(
            f"""
            You are the Planner Agent. Read AGENTS.md and the TaskPack content below.
            Produce a concise plan as markdown and write it to {tp.path.as_posix()}/plan.md.
            Do not modify source code in this phase.

            {ctx}
            """
        ).strip()

    if phase == "implementer":
        return textwrap.dedent(
            f"""
            You are the Implementer Agent. Read AGENTS.md, TEAM_GUIDE.md and the TaskPack content below.
            Use skills if helpful (preferred: {", ".join(tp.preferred_skills) or "none"}).
            Implement the task. Keep changes small and testable.
            If you need to run commands, prefer the ones listed in acceptance.yml.
            Do NOT introduce secrets. Do NOT expand scope beyond the TaskPack.
            After implementation, summarize changes in {tp.path.as_posix()}/change_summary.md.

            {ctx}
            """
        ).strip()

    if phase == "verifier":
        return textwrap.dedent(
            f"""
            You are the Verifier Agent. Read AGENTS.md and the TaskPack content below.
            Ensure the implementation meets acceptance criteria and add minimal regression tests if missing.
            Focus on reproducibility. Update {tp.path.as_posix()}/verification_notes.md with findings.

            {ctx}
            """
        ).strip()

    if phase == "security":
        return textwrap.dedent(
            f"""
            You are the Security Agent. Read AGENTS.md and the TaskPack content below.
            Look for common security pitfalls: secret leaks, unsafe defaults, injection risks, logging of secrets,
            weak crypto, insecure subprocess usage, missing input validation, and supply-chain hazards.
            Add or recommend mitigations. Write findings to {tp.path.as_posix()}/security_review.md.

            {ctx}
            """
        ).strip()

    if phase == "pr_author":
        return textwrap.dedent(
            f"""
            You are the PR Author Agent. Use the 'pr-author' skill.
            Write a PR body (markdown) to {tp.path.as_posix()}/pr_body.md including:
            - Summary (what/why)
            - Testing evidence (commands)
            - Risk/rollback notes
            - Checklist

            {ctx}
            """
        ).strip()

    raise ValueError(f"Unknown phase: {phase}")


def run_acceptance(
    tp: TaskPack,
    *,
    workspace_root: pathlib.Path,
    log_dir: pathlib.Path,
) -> list[dict[str, str]]:
    # Ground-truth execution outside Codex.
    acc = tp.acceptance or {}
    deps = acc.get("deps", []) or []
    results: list[dict[str, str]] = []
    
    if deps:
        run("python -m pip install --upgrade pip", check=True, cwd=workspace_root)
        run(
            "python -m pip install --disable-pip-version-check "
            + " ".join(map(shlex.quote, deps)),
            check=True,
            cwd=workspace_root,
        )

    sections = [
        ("format", acc.get("format", {})),
        ("lint", acc.get("lint", {})),
        ("tests", acc.get("tests", {})),
    ]    
        
    for name, section in sections:
        cmds = section.get("commands", []) if isinstance(section, dict) else []
        for i, cmd in enumerate(cmds):
            log = log_dir / f"acceptance_{name}_{i}.log"
            try:
                out = run(cmd, check=True, cwd=workspace_root)
                log.write_text(out.stdout or "", encoding="utf-8")
                results.append(
                    {
                        "section": name,
                        "command": cmd,
                        "status": "pass",
                        "log_path": str(log),
                    }
                )
            except subprocess.CalledProcessError as e:
                log.write_text(e.stdout or "", encoding="utf-8")

                # pytest returns 5 when no tests are collected
                if "pytest" in cmd and e.returncode == 5:
                    warn = log_dir / "acceptance_warnings.log"
                    warn.write_text(
                        "pytest reported no tests collected (exit code 5)\n",
                        encoding="utf-8",
                    )
                    results.append(
                        {
                            "section": name,
                            "command": cmd,
                            "status": "warning",
                            "log_path": str(log),
                        }
                    )
                    return results
                results.append(
                    {
                        "section": name,
                        "command": cmd,
                        "status": "fail",
                        "log_path": str(log),
                    }
                )
                raise
    return results

def ensure_https_remote_for_ci(*, cwd: pathlib.Path) -> None:
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        repo = os.getenv("GITHUB_REPOSITORY")  # e.g. owner/name
        if not repo:
            return
        # Use token auth; GitHub Actions provides GITHUB_TOKEN
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if not token:
            return
        run(
            f"git remote set-url origin https://x-access-token:{token}@github.com/{repo}.git",
            check=True,
            cwd=cwd,
        )

def gh_pr_exists_for_head(branch: str, *, cwd: pathlib.Path) -> bool:
    proc = run(
        f"gh pr list --head {shlex.quote(branch)} --json number -q 'length'",
        check=False,
        cwd=cwd,
    )
    return proc.returncode == 0 and (proc.stdout or "").strip() not in ("", "0")

def git_checkout_branch(branch: str, *, cwd: pathlib.Path) -> None:
    # Create branch if it doesn't exist; otherwise just checkout
    proc = run(f"git rev-parse --verify {shlex.quote(branch)}", check=False, cwd=cwd)
    if proc.returncode == 0:
        run(f"git checkout {shlex.quote(branch)}", cwd=cwd)
    else:
        run(f"git checkout -b {shlex.quote(branch)}", cwd=cwd)

def main() -> None:

    args = parse_args(sys.argv[1:])
    enable_plugins = args.enable_plugins or _env_truthy("ORCH_ENABLE_PLUGINS")
    plugins_strict = args.plugins_strict or _env_truthy("ORCH_PLUGINS_STRICT")
    collect_review = _env_truthy("ORCH_COLLECT_REVIEW")
    write_evidence_index = _env_truthy("ORCH_WRITE_EVIDENCE_INDEX")

    taskpack_path = pathlib.Path(must_env("TASKPACK_PATH")).resolve()
    if not taskpack_path.exists():
        raise SystemExit(f"TASKPACK_PATH does not exist: {taskpack_path}")

    max_attempts = int(os.getenv("MAX_ATTEMPTS", "2"))
    branch_prefix = os.getenv("BRANCH_PREFIX", "codex")

    tp = load_taskpack(taskpack_path)

    workspace_spec = select_workspace_spec(
        cli_value=args.workspace,
        env_value=os.getenv("ORCH_WORKSPACE"),
        task_value=tp.task.get("workspace"),
    )
    registry_path = ROOT / "workspaces" / "registry.yml"
    try:
        workspace = resolve_workspace(
            spec=workspace_spec,
            registry_path=registry_path,
            default_root=ROOT,
        )
    except WorkspaceRegistryError as exc:
        raise SystemExit(str(exc)) from exc

    workspace_root = workspace.root
    evidence_root, log_dir = evidence_paths(workspace, run_id=f"{tp.id.lower()}-{int(time.time())}")

    if workspace_root != ROOT:
        if _is_relative_to(evidence_root.resolve(), ROOT.resolve()):
            raise SystemExit("Managed repo evidence must not be written inside the playbook repo.")

    run_id = log_dir.name

    global LOG_DIR, LOG_ROOT
    LOG_ROOT = evidence_root
    LOG_DIR = log_dir
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    ensure_managed_repo_contracts(tp, workspace_root=workspace_root, playbook_root=ROOT)
    ensure_required_docs(tp, workspace_root=workspace_root)

    manifest_path = LOG_DIR / "manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text('{"result":"started"}\n', encoding="utf-8")

    manifest = {"result": "started", "run_id": run_id}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {"result": "started", "warning": "manifest_unreadable", "run_id": run_id}
    if "run_id" not in manifest:
        manifest["run_id"] = run_id
    _write_manifest(manifest_path, manifest)

    manifest_repo_root = workspace_root if _is_relative_to(evidence_root, workspace_root) else evidence_root

    starting_branch = git_current_branch(cwd=workspace_root)
    base_branch = os.getenv("BASE_BRANCH") or starting_branch

    explicit_branch = os.getenv("ORCH_BRANCH_NAME")
    branch_name = explicit_branch or f"{branch_prefix}/{tp.id.lower()}-{int(time.time())}"

    git_checkout_branch(branch_name, cwd=workspace_root)

    run_codex = os.getenv("RUN_CODEX_SMOKE", "false").lower() == "true"

    plugin_spec = tp.task.get("plugin")

    manifest["plugins_enabled"] = bool(enable_plugins)
    manifest["plugin"] = {"spec": plugin_spec, "status": "SKIPPED"}
    _write_manifest(manifest_path, manifest)

    if enable_plugins:
        if not plugin_spec:
            manifest["plugin"] = {"spec": None, "status": "SKIPPED", "reason": "taskpack.task.plugin missing"}
            _write_manifest(manifest_path, manifest)
        else:
            artifact_dir = LOG_DIR / "plugin" / tp.id
            try:
                ctx = _make_execution_context(
                    tp,
                    run_id=run_id,
                    workspace_dir=workspace_root,
                    artifact_dir=artifact_dir,
                    log_dir=LOG_DIR,
                )
                plugin_result = run_plugin(tp.task, ctx)
                manifest["plugin"] = {
                    "spec": plugin_spec,
                    "status": plugin_result.get("status", "UNKNOWN"),
                    "result_path": _path_for_manifest(
                        pathlib.Path(ctx.artifact_dir) / "plugin_result.json",
                        repo_root=manifest_repo_root,
                    ),
                    "id": plugin_result.get("plugin", {}).get("id"),
                    "version": plugin_result.get("plugin", {}).get("version"),
                }
                _write_manifest(manifest_path, manifest)
            except Exception as e:
                manifest["plugin"] = {"spec": plugin_spec, "status": "ERROR", "errors": [{"error": str(e)}]}
                _write_manifest(manifest_path, manifest)
                if plugins_strict:
                    raise
        print(f"[plugin] {plugin_spec} -> {manifest['plugin']['status']}")

    phases = ["planner", "implementer", "verifier", "security", "pr_author"]

    for phase in phases:
        if not run_codex:
            print(f"[skip] Codex phase '{phase}' (RUN_CODEX_SMOKE=false)")
            continue
        ok = False
        for attempt in range(1, max_attempts + 1):
            prompt = phase_prompt(tp, phase)
            rc, out = codex_exec(
                prompt,
                log_name=f"{phase}_attempt{attempt}",
                cwd=workspace_root,
                log_dir=LOG_DIR,
            )
            if rc == 0:
                ok = True
                break
            # Retry strategy: narrow scope on later attempts
            # (keeps it simple in Draft 1; we’ll expand reroute logic in Draft 2)
            time.sleep(2)

        if not ok:
            # Commit whatever we have (so we can inspect diffs in PR if desired)
            git_commit(f"chore: partial changes before failure in {phase}", cwd=workspace_root)
            ensure_https_remote_for_ci(cwd=workspace_root)
            run("git push -u origin HEAD", cwd=workspace_root)
            raise SystemExit(f"Phase failed after {max_attempts} attempts: {phase}")

        # Commit after key phases (planner writes files; still commit for traceability)
        if phase in ("planner", "implementer", "verifier", "security"):
            git_commit(f"chore: {phase} outputs for {tp.id}", cwd=workspace_root)

    # Run acceptance checks (ground truth)
    acceptance_results = run_acceptance(tp, workspace_root=workspace_root, log_dir=LOG_DIR)
    enforce_scope_allowed_paths(tp, workspace_root=workspace_root, base_ref=starting_branch)
    git_commit(f"test: acceptance checks pass for {tp.id}", cwd=workspace_root)

    if collect_review:
        _collect_review_report(
            manifest,
            manifest_path=manifest_path,
            log_dir=LOG_DIR,
            repo_root=manifest_repo_root,
            cwd=workspace_root,
        )
    _maybe_collect_evidence_index(
        write_evidence_index,
        manifest,
        manifest_path=manifest_path,
        evidence_root=evidence_root,
        repo_root=manifest_repo_root,
    )

    # Push branch and open PR
    ensure_https_remote_for_ci(cwd=workspace_root)
    run("git push -u origin HEAD", cwd=workspace_root)

    pr_body_path = tp.path / "pr_body.md"
    extra_body = None
    if pr_body_path.exists():
        extra_body = pr_body_path.read_text(encoding="utf-8")
    pr_body = build_pr_body(
        tp,
        branch_name=branch_name,
        base_branch=base_branch,
        evidence_root=evidence_root,
        run_id=run_id,
        acceptance_results=acceptance_results,
        workspace_root=workspace_root,
        extra_body=extra_body,
    )

    title = f"{tp.id}: {tp.title}"
    if gh_pr_exists_for_head(branch_name, cwd=workspace_root):
        print("PR already exists for this branch; skipping creation.")
    else:
        pr_out = gh_pr_create(
            title=title,
            body=pr_body,
            base=base_branch,
            cwd=workspace_root,
            log_dir=LOG_DIR,
        )
        print(f"PR: {pr_out}")

    manifest["result"] = "success"
    _write_manifest(manifest_path, manifest)
    print(f"Done. Branch: {branch_name}")


if __name__ == "__main__":
    main()
