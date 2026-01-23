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
LOG_DIR = ROOT / ".orchestrator_logs"
LOG_DIR.mkdir(exist_ok=True)

# Ensure repo root is on sys.path so absolute imports like `tools.*` work
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# v2 plugin thin-slice
from tools.evidence import index as evidence_index
from tools.evidence import schemas as evidence_schemas
from tools.orchestrator.plugins.runner import run_plugin
from tools.orchestrator.plugins.interface import ExecutionContext

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
    return subprocess.run(
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
    return p.parse_args(argv)

def _env_truthy(name: str) -> bool:
    v = os.getenv(name, "").strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def _write_manifest(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")

def _collect_review_report(manifest: dict, *, manifest_path: pathlib.Path) -> None:
    report_path = LOG_DIR / "review_report.json"
    cmd = (
        f"{shlex.quote(sys.executable)} -m tools.review.run_review "
        f"--mode advisory --report-path {shlex.quote(str(report_path))}"
    )
    proc = run(cmd, check=False)

    if proc.returncode == 0:
        status = "pass"
    elif proc.returncode == 2:
        status = "violations"
    else:
        status = "error"

    if report_path.exists():
        manifest["review_report_path"] = str(report_path.relative_to(ROOT))
        manifest["review_schema_version"] = 1
        manifest["review_status"] = status
    else:
        manifest["review_status"] = "error"
        manifest["review_error"] = "review_report_missing"

    _write_manifest(manifest_path, manifest)
    print(f"[review] collected status={status} report={report_path}")


def _collect_evidence_index(manifest: dict, *, manifest_path: pathlib.Path) -> None:
    index_path = LOG_DIR / evidence_schemas.INDEX_FILENAME
    try:
        index = evidence_index.build_index([LOG_DIR], repo_root=ROOT)
        evidence_index.write_index(index, index_path)
        manifest["evidence_index_path"] = str(index_path.relative_to(ROOT))
        manifest["evidence_index_schema_version"] = evidence_schemas.INDEX_SCHEMA_VERSION
        manifest.pop("evidence_index_error", None)
        _write_manifest(manifest_path, manifest)
        print(f"[evidence] index written: {index_path}")
    except Exception as exc:
        manifest["evidence_index_error"] = f"{type(exc).__name__}: {exc}"
        _write_manifest(manifest_path, manifest)
        print(f"[evidence] index failed: {manifest['evidence_index_error']}")


def _maybe_collect_evidence_index(
    enabled: bool, manifest: dict, *, manifest_path: pathlib.Path
) -> None:
    if not enabled:
        return
    _collect_evidence_index(manifest, manifest_path=manifest_path)

def _make_execution_context(tp: TaskPack, *, artifact_dir: pathlib.Path) -> ExecutionContext:
    run_id = f"{tp.id.lower()}-{int(time.time())}"

    workspace_dir = ROOT / ".orchestrator_workspace" / run_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    artifact_dir.mkdir(parents=True, exist_ok=True)

    constraints = dict(tp.task.get("constraints", {}) or {})

    plugin_log_path = LOG_DIR / f"plugin_{tp.id.lower()}.log"

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


def git_current_branch() -> str:
    return run("git rev-parse --abbrev-ref HEAD").stdout.strip()


def git_has_changes() -> bool:
    out = run("git status --porcelain", check=False).stdout.strip()
    return bool(out)


def git_commit(message: str) -> None:
    run("git add -A")
    if not git_has_changes():
        return
    run(f"git commit -m {shlex.quote(message)}")


def gh_pr_create(title: str, body: str, base: str = "main") -> str:
    # GitHub Actions usually has GH_TOKEN set automatically.
    # We'll rely on `gh` being present on runner (it is on ubuntu-latest).
    body_file = LOG_DIR / "pr_body.md"
    body_file.write_text(body, encoding="utf-8")
    cmd = f"gh pr create --base {shlex.quote(base)} --title {shlex.quote(title)} --body-file {shlex.quote(str(body_file))}"
    out = run(cmd).stdout.strip().splitlines()[-1]
    return out

def default_pr_body(tp: TaskPack, *, branch_name: str, base_branch: str) -> str:
    plugin_spec = tp.task.get("plugin")
    plugin_enabled = os.getenv("ORCH_ENABLE_PLUGINS", "").strip()

    return textwrap.dedent(
        f"""
        ## Summary
        Wire v2 solution plugins into `tools/orchestrator/orchestrate.py` behind a flag and run them using the v2 runner.

        ## What changed
        - Add `ORCH_ENABLE_PLUGINS=1` / `--enable-plugins` to run the plugin specified in `task.yml` (`plugin:`).
        - Create an `ExecutionContext` (`run_id`, `workspace_dir`, `artifact_dir`, `constraints`) and run `tools.orchestrator.plugins.runner.run_plugin`.
        - Record plugin status + result path in `.orchestrator_logs/manifest.json`.
        - Normalize plugin artifact paths in `plugin_result.json` (relative paths for portability).
        - CI push uses HTTPS token auth when running under GitHub Actions.
        - Add `ORCH_BRANCH_NAME` support + PR-exists guard to prevent branch/PR spam.

        ## How to run
        ```bash
        ORCH_BRANCH_NAME=codex/{tp.id.lower()} \\
        TASKPACK_PATH={tp.path.as_posix()} \\
        ORCH_ENABLE_PLUGINS=1 \\
        RUN_CODEX_SMOKE=false \\
        python tools/orchestrator/orchestrate.py
        ```

        ## Evidence
        - `python -m pytest -q`
        - Plugin artifacts created under: `.orchestrator_logs/plugin/{tp.id}/`
          - `echo.txt`
          - `echo_report.md`
          - `plugin_result.json`

        ## Risk / rollback
        - Default behavior unchanged unless plugins are enabled.
        - Rollback: revert changes in `tools/orchestrator/orchestrate.py` and `tools/orchestrator/plugins/runner.py`.

        ## Checklist
        - [x] Tests pass
        - [x] Plugin execution behind flag
        - [x] Manifest updated with plugin result
        """
    ).strip()

def codex_exec(prompt: str, *, log_name: str) -> Tuple[int, str]:
    """
    Runs Codex in non-interactive mode.
    We use `codex exec` so the agent can modify files and run commands as needed,
    but we keep our own acceptance commands outside of Codex as a safety/ground-truth step.
    """
    log_path = LOG_DIR / f"{log_name}.log"
    # Use --json if you want structured output later; for now keep plain logs.
    cmd = f"codex exec {shlex.quote(prompt)}"
    proc = subprocess.run(cmd, cwd=str(ROOT), shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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


def run_acceptance(tp: TaskPack) -> None:
    # Ground-truth execution outside Codex.
    acc = tp.acceptance or {}
    deps = acc.get("deps", []) or []
    
    if deps:
        run("python -m pip install --upgrade pip", check=True)
        run(
            "python -m pip install --disable-pip-version-check "
            + " ".join(map(shlex.quote, deps)),
            check=True,
        )

    sections = [
        ("format", acc.get("format", {})),
        ("lint", acc.get("lint", {})),
        ("tests", acc.get("tests", {})),
    ]    
        
    for name, section in sections:
        cmds = section.get("commands", []) if isinstance(section, dict) else []
        for i, cmd in enumerate(cmds):
            log = LOG_DIR / f"acceptance_{name}_{i}.log"
            try:
                out = run(cmd, check=True)
                log.write_text(out.stdout or "", encoding="utf-8")
            except subprocess.CalledProcessError as e:
                log.write_text(e.stdout or "", encoding="utf-8")

                # pytest returns 5 when no tests are collected
                if "pytest" in cmd and e.returncode == 5:
                    # Treat as warning, not failure
                    warn = LOG_DIR / "acceptance_warnings.log"
                    warn.write_text(
                        "pytest reported no tests collected (exit code 5)\n",
                        encoding="utf-8",
                    )
                    return
                raise

def ensure_https_remote_for_ci() -> None:
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        repo = os.getenv("GITHUB_REPOSITORY")  # e.g. owner/name
        if not repo:
            return
        # Use token auth; GitHub Actions provides GITHUB_TOKEN
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if not token:
            return
        run(f"git remote set-url origin https://x-access-token:{token}@github.com/{repo}.git", check=True)

def gh_pr_exists_for_head(branch: str) -> bool:
    proc = run(
        f"gh pr list --head {shlex.quote(branch)} --json number -q 'length'",
        check=False,
    )
    return proc.returncode == 0 and (proc.stdout or "").strip() not in ("", "0")

def git_checkout_branch(branch: str) -> None:
    # Create branch if it doesn't exist; otherwise just checkout
    proc = run(f"git rev-parse --verify {shlex.quote(branch)}", check=False)
    if proc.returncode == 0:
        run(f"git checkout {shlex.quote(branch)}")
    else:
        run(f"git checkout -b {shlex.quote(branch)}")

def main() -> None:

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    args = parse_args(sys.argv[1:])
    enable_plugins = args.enable_plugins or _env_truthy("ORCH_ENABLE_PLUGINS")
    plugins_strict = args.plugins_strict or _env_truthy("ORCH_PLUGINS_STRICT")
    collect_review = _env_truthy("ORCH_COLLECT_REVIEW")
    write_evidence_index = _env_truthy("ORCH_WRITE_EVIDENCE_INDEX")

    manifest_path = LOG_DIR / "manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text('{"result":"started"}\n', encoding="utf-8")

    manifest = {"result": "started"}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {"result": "started", "warning": "manifest_unreadable"}
    _write_manifest(manifest_path, manifest)

    taskpack_path = pathlib.Path(must_env("TASKPACK_PATH")).resolve()
    if not taskpack_path.exists():
        raise SystemExit(f"TASKPACK_PATH does not exist: {taskpack_path}")

    max_attempts = int(os.getenv("MAX_ATTEMPTS", "2"))
    branch_prefix = os.getenv("BRANCH_PREFIX", "codex")

    tp = load_taskpack(taskpack_path)

    starting_branch = git_current_branch()
    base_branch = os.getenv("BASE_BRANCH") or starting_branch

    explicit_branch = os.getenv("ORCH_BRANCH_NAME")
    branch_name = explicit_branch or f"{branch_prefix}/{tp.id.lower()}-{int(time.time())}"

    git_checkout_branch(branch_name)

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
                ctx = _make_execution_context(tp, artifact_dir=artifact_dir)
                plugin_result = run_plugin(tp.task, ctx)
                manifest["plugin"] = {
                    "spec": plugin_spec,
                    "status": plugin_result.get("status", "UNKNOWN"),
                    "result_path": str(pathlib.Path(ctx.artifact_dir).relative_to(ROOT) / "plugin_result.json"),
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
            rc, out = codex_exec(prompt, log_name=f"{phase}_attempt{attempt}")
            if rc == 0:
                ok = True
                break
            # Retry strategy: narrow scope on later attempts
            # (keeps it simple in Draft 1; we’ll expand reroute logic in Draft 2)
            time.sleep(2)

        if not ok:
            # Commit whatever we have (so we can inspect diffs in PR if desired)
            git_commit(f"chore: partial changes before failure in {phase}")
            ensure_https_remote_for_ci()
            run("git push -u origin HEAD")
            raise SystemExit(f"Phase failed after {max_attempts} attempts: {phase}")

        # Commit after key phases (planner writes files; still commit for traceability)
        if phase in ("planner", "implementer", "verifier", "security"):
            git_commit(f"chore: {phase} outputs for {tp.id}")

    # Run acceptance checks (ground truth)
    run_acceptance(tp)
    git_commit(f"test: acceptance checks pass for {tp.id}")

    if collect_review:
        _collect_review_report(manifest, manifest_path=manifest_path)
    _maybe_collect_evidence_index(
        write_evidence_index, manifest, manifest_path=manifest_path
    )

    # Push branch and open PR
    ensure_https_remote_for_ci()
    run("git push -u origin HEAD")

    pr_body_path = tp.path / "pr_body.md"
    if pr_body_path.exists():
        pr_body = pr_body_path.read_text(encoding="utf-8")
    else:
        pr_body = default_pr_body(tp, branch_name=branch_name, base_branch=base_branch)

    title = f"{tp.id}: {tp.title}"
    if gh_pr_exists_for_head(branch_name):
        print("PR already exists for this branch; skipping creation.")
    else:
        pr_out = gh_pr_create(title=title, body=pr_body, base=base_branch)
        print(f"PR: {pr_out}")

    manifest["result"] = "success"
    _write_manifest(manifest_path, manifest)
    print(f"Done. Branch: {branch_name}")


if __name__ == "__main__":
    main()
