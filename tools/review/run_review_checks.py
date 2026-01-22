#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
from typing import Iterable

ALLOWED_PREFIXES = (
    ".github/workflows/",
    "docs/",
    "solutions/",
    "taskpacks/",
    "tools/acceptance/",
    "tools/review/",
    "scripts/",
    "tests/",
    ".codex/skills/",
)

ALLOWED_FILES = {
    "AGENTS.md",
    "README.md",
    "pytest.ini",
}

ORCHESTRATOR_ALLOWLIST = {
    # Add explicit paths here if orchestrator changes are approved.
}

TIER1_DOCS = {
    "docs/Current Status.md": {"non_empty": True},
    "docs/GOVERNANCE.md": {"non_empty": False},
    "docs/Canonical Conventions.md": {"non_empty": False},
}

REQUIRED_PATHS_FOR_TIER1_CHECK = (
    "solutions/",
    "taskpacks/",
    "tools/orchestrator/",
)


def run_cmd(cmd: list[str], env: dict[str, str] | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    return proc.returncode, proc.stdout.strip()


def git_ref_exists(ref: str) -> bool:
    code, _ = run_cmd(["git", "rev-parse", "--verify", ref])
    return code == 0


def resolve_base_ref(explicit_ref: str | None) -> str:
    if explicit_ref:
        return explicit_ref
    if git_ref_exists("origin/main"):
        return "origin/main"
    if git_ref_exists("main"):
        return "main"
    return "HEAD"


def get_changed_files(base_ref: str) -> tuple[list[str], str | None]:
    code, output = run_cmd(["git", "diff", "--name-only", f"{base_ref}...HEAD"])
    if code != 0:
        return [], output
    files = [line.strip() for line in output.splitlines() if line.strip()]
    return files, None


def format_list(title: str, items: Iterable[str]) -> list[str]:
    lines = [title]
    for item in items:
        lines.append(f" - {item}")
    if len(lines) == 1:
        lines.append(" - (none)")
    return lines


def check_scope(changed_files: list[str]) -> tuple[list[str], bool]:
    lines: list[str] = []
    hard_fail = False

    orchestrator_hits = [
        f for f in changed_files if f.startswith("tools/orchestrator/") and f not in ORCHESTRATOR_ALLOWLIST
    ]
    if orchestrator_hits:
        hard_fail = True
        lines.append("[FAIL] Orchestrator path change blocked by allowlist rule")
        lines.extend(format_list("Offending paths:", orchestrator_hits))
        lines.append("Rule: changes under tools/orchestrator/ require explicit allowlist")
    else:
        lines.append("[PASS] Orchestrator path allowlist")

    out_of_scope = []
    for f in changed_files:
        if f in ALLOWED_FILES:
            continue
        if f.startswith(ALLOWED_PREFIXES):
            continue
        out_of_scope.append(f)

    if out_of_scope:
        hard_fail = True
        lines.append("[FAIL] Out-of-scope path change detected")
        lines.extend(format_list("Offending paths:", out_of_scope))
        lines.append("Rule: changes must remain within approved path prefixes")
    else:
        lines.append("[PASS] Allowed path prefixes")

    return lines, hard_fail


def check_tier1_docs(changed_files: list[str]) -> tuple[list[str], bool]:
    lines: list[str] = []
    hard_fail = False

    touches_required = any(
        f.startswith(REQUIRED_PATHS_FOR_TIER1_CHECK) for f in changed_files
    )
    if not touches_required:
        lines.append("[SKIP] Tier-1 docs presence (no scoped changes detected)")
        return lines, hard_fail

    lines.append("[CHECK] Tier-1 docs presence")
    for path_str, rules in TIER1_DOCS.items():
        path = Path(path_str)
        if not path.exists():
            lines.append(f"[FAIL] Missing required doc: {path_str}")
            hard_fail = True
            continue
        if rules.get("non_empty"):
            try:
                content = path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                lines.append(f"[FAIL] Unable to read {path_str}: {exc}")
                hard_fail = True
                continue
            if not content:
                lines.append(f"[FAIL] Required doc is empty: {path_str}")
                hard_fail = True
                continue
        lines.append(f"[PASS] {path_str}")

    return lines, hard_fail


def copy_changed_files(changed_files: list[str]) -> Path | None:
    if not changed_files:
        return None
    temp_dir = Path(tempfile.mkdtemp(prefix="review-checks-"))
    for rel_path in changed_files:
        src = Path(rel_path)
        if not src.exists() or not src.is_file():
            continue
        dest = temp_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return temp_dir


def check_forbidden_language(changed_files: list[str]) -> tuple[list[str], bool]:
    lines: list[str] = []
    hard_fail = False

    scoped_root = copy_changed_files(changed_files)
    if scoped_root is None:
        return ["[SKIP] Forbidden language checks (no changed files)"], False

    checks = [
        [sys.executable, "tools/acceptance/check_no_qualitative_language.py", "--path", str(scoped_root)],
        [sys.executable, "tools/acceptance/check_no_deploy_language.py", "--path", str(scoped_root)],
    ]
    for cmd in checks:
        code, output = run_cmd(cmd)
        label = " ".join(cmd)
        if code != 0:
            hard_fail = True
            lines.append(f"[FAIL] {label}")
            if output:
                lines.extend(format_list("Output:", output.splitlines()))
        else:
            lines.append(f"[PASS] {label}")

    shutil.rmtree(scoped_root, ignore_errors=True)
    return lines, hard_fail


def check_compileall() -> tuple[list[str], bool]:
    code, output = run_cmd([sys.executable, "-m", "compileall", "-q", "."])
    if code != 0:
        lines = ["[FAIL] python -m compileall -q ."]
        if output:
            lines.extend(format_list("Output:", output.splitlines()))
        return lines, True
    return ["[PASS] python -m compileall -q ."], False


def check_tests(mode: str) -> tuple[list[str], bool]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "." + os.pathsep + env.get("PYTHONPATH", "")

    if mode == "fast":
        cmd = ["pytest", "-q", "tests/test_taskpack_canaries.py"]
    else:
        cmd = ["pytest", "-q"]

    code, output = run_cmd(cmd, env=env)
    label = " ".join(cmd)
    if code != 0:
        lines = [f"[FAIL] {label}"]
        if output:
            lines.extend(format_list("Output:", output.splitlines()))
        return lines, True
    return [f"[PASS] {label}"], False


def write_report(report_text: str, report_file: str | None) -> None:
    if not report_file:
        return
    path = Path(report_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--fast", action="store_true", help="Run fast checks (default)")
    mode.add_argument("--full", action="store_true", help="Run full checks")
    ap.add_argument("--base-ref", help="Git base ref for diff")
    ap.add_argument("--report-file", help="Write report to a file path")
    args = ap.parse_args()

    selected_mode = "full" if args.full else "fast"
    base_ref = resolve_base_ref(args.base_ref)

    report_lines = ["Review Checks Report", f"Mode: {selected_mode}", f"Base ref: {base_ref}"]

    if run_cmd(["git", "rev-parse", "--is-inside-work-tree"])[0] != 0:
        report_lines.append("[FAIL] Git repository not detected")
        report_text = "\n".join(report_lines)
        print(report_text)
        write_report(report_text, args.report_file)
        return 2

    changed_files, diff_error = get_changed_files(base_ref)
    if diff_error is not None:
        report_lines.append("[FAIL] Unable to compute git diff")
        report_lines.extend(format_list("Git output:", diff_error.splitlines()))
        report_text = "\n".join(report_lines)
        print(report_text)
        write_report(report_text, args.report_file)
        return 2

    report_lines.extend(format_list("Changed files:", changed_files))

    failures = False

    scope_lines, scope_fail = check_scope(changed_files)
    report_lines.append("Scope & Boundary Checks:")
    report_lines.extend(scope_lines)
    failures = failures or scope_fail

    tier_lines, tier_fail = check_tier1_docs(changed_files)
    report_lines.append("Tier-1 Documentation Checks:")
    report_lines.extend(tier_lines)
    failures = failures or tier_fail

    compile_lines, compile_fail = check_compileall()
    report_lines.append("Compile Checks:")
    report_lines.extend(compile_lines)
    failures = failures or compile_fail

    test_lines, test_fail = check_tests(selected_mode)
    report_lines.append("Test Checks:")
    report_lines.extend(test_lines)
    failures = failures or test_fail

    forbidden_lines, forbidden_fail = check_forbidden_language(changed_files)
    report_lines.append("Forbidden Language Checks:")
    report_lines.extend(forbidden_lines)
    failures = failures or forbidden_fail

    report_text = "\n".join(report_lines)
    print(report_text)
    write_report(report_text, args.report_file)

    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
