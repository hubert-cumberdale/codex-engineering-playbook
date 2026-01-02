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
        check=check,
    )


def must_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v


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


def gh_pr_create(title: str, body: str, base: str = "main") -> None:
    # GitHub Actions usually has GH_TOKEN set automatically.
    # We'll rely on `gh` being present on runner (it is on ubuntu-latest).
    body_file = LOG_DIR / "pr_body.md"
    body_file.write_text(body, encoding="utf-8")
    cmd = f"gh pr create --base {shlex.quote(base)} --title {shlex.quote(title)} --body-file {shlex.quote(str(body_file))}"
    run(cmd)


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
    deps = acc.get("deps", [])
    if deps:
        run(f"python -m pip install {' '.join(deps)}", check=True)
    sections = [("format", acc.get("format", {})), ("lint", acc.get("lint", {})), ("tests", acc.get("tests", {}))]
    for name, section in sections:
        cmds = section.get("commands", []) if isinstance(section, dict) else []
        for i, cmd in enumerate(cmds):
            log = LOG_DIR / f"acceptance_{name}_{i}.log"
            try:
                out = run(cmd, check=True)
                log.write_text((out.stdout or "") + (out.stderr or ""), encoding="utf-8")
            except subprocess.CalledProcessError as e:
                log.write_text((e.stdout or "") + (e.stderr or ""), encoding="utf-8")
                raise


def main() -> None:

    # Ensure logs dir exists immediately so the workflow can always upload artifacts
    log_dir = Path(".orchestrator_logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Always write a minimal manifest early
    manifest_path = log_dir / "manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text('{"result":"started"}\n', encoding="utf-8")

    # Ensure logs dir exists immediately so the workflow can always upload artifacts
    log_dir = Path(".orchestrator_logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Always write a minimal manifest early
    manifest_path = log_dir / "manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text('{"result":"started"}\n', encoding="utf-8")
    taskpack_path = pathlib.Path(must_env("TASKPACK_PATH")).resolve()
    if not taskpack_path.exists():
        raise SystemExit(f"TASKPACK_PATH does not exist: {taskpack_path}")

    max_attempts = int(os.getenv("MAX_ATTEMPTS", "2"))
    branch_prefix = os.getenv("BRANCH_PREFIX", "codex")

    tp = load_taskpack(taskpack_path)

    base_branch = git_current_branch()
    branch_name = f"{branch_prefix}/{tp.id.lower()}-{int(time.time())}"
    run(f"git checkout -b {shlex.quote(branch_name)}")

    phases = ["planner", "implementer", "verifier", "security", "pr_author"]

    for phase in phases:
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
            run("git push -u origin HEAD")
            raise SystemExit(f"Phase failed after {max_attempts} attempts: {phase}")

        # Commit after key phases (planner writes files; still commit for traceability)
        if phase in ("planner", "implementer", "verifier", "security"):
            git_commit(f"chore: {phase} outputs for {tp.id}")

    # Run acceptance checks (ground truth)
    run_acceptance(tp)
    git_commit(f"test: acceptance checks pass for {tp.id}")

    # Push branch and open PR
    run("git push -u origin HEAD")

    pr_body_path = tp.path / "pr_body.md"
    pr_body = pr_body_path.read_text(encoding="utf-8") if pr_body_path.exists() else "(PR body not generated.)"

    title = f"{tp.id}: {tp.title}"
    gh_pr_create(title=title, body=pr_body, base=base_branch)

    print(f"Done. Opened PR for branch: {branch_name}")


if __name__ == "__main__":
    main()
