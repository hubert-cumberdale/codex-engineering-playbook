#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

TOKENS = ["engine", "engine_version", "godot", "unity"]

def contains_any(path: Path) -> bool:
    if not path.exists():
        return False
    data = path.read_text(encoding="utf-8", errors="ignore").lower()
    return any(t in data for t in TOKENS)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-yml", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--artifact-path", required=True)
    args = ap.parse_args()

    ok = (
        contains_any(Path(args.task_yml))
        or contains_any(Path(args.spec))
    )

    # Also accept if artifacts declare engine intent
    art = Path(args.artifact_path)
    if art.exists() and art.is_dir():
        for f in art.rglob("*"):
            if f.is_file() and contains_any(f):
                ok = True
                break

    if not ok:
        print("[acceptance] FAIL: engine/version intent not declared (expected one of tokens: "
              + ", ".join(TOKENS) + ")")
        return 2

    print("[acceptance] OK: engine/version intent declared")
    return 0

if __name__ == "__main__":
    sys.exit(main())
