#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys

def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout.strip()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allowed", nargs="+", required=True, help="Allowed path prefixes (e.g., taskpacks/)")
    args = ap.parse_args()

    allowed = tuple(a if a.endswith("/") else a + "/" for a in args.allowed)

    # Use staged+unstaged; in CI the working tree reflects changes
    out = run(["git", "diff", "--name-only", "HEAD"])
    files = [line.strip() for line in out.splitlines() if line.strip()]

    violations = [f for f in files if not f.startswith(allowed)]
    if violations:
        print("[acceptance] FAIL: diff scope violation; modified files outside allowed prefixes:")
        for v in violations:
            print(f" - {v}")
        return 2

    print("[acceptance] OK: diff scope within allowed prefixes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
