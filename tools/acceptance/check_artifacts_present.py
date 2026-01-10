#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Artifacts directory (relative to CWD)")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists() or not p.is_dir():
        print(f"[acceptance] FAIL: artifacts dir missing: {p}")
        return 2

    # Any file under artifacts/** counts (excluding directories)
    files = [f for f in p.rglob("*") if f.is_file()]
    if not files:
        print(f"[acceptance] FAIL: no artifacts found under: {p}")
        return 3

    print(f"[acceptance] OK: {len(files)} artifact file(s) present under {p}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
