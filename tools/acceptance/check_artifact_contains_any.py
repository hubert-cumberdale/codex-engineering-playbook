#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

TEXT_EXTS = {".txt", ".md", ".log", ".json", ".yml", ".yaml", ".csv"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--any", nargs="+", required=True, help="Any of these tokens must appear (case-insensitive)")
    args = ap.parse_args()

    root = Path(args.path)
    tokens = [t.lower() for t in args.any]

    files = [f for f in root.rglob("*") if f.is_file() and (f.suffix.lower() in TEXT_EXTS or f.suffix == "")]
    if not files:
        print(f"[acceptance] FAIL: no readable artifact files under {root}")
        return 2

    for f in files:
        try:
            data = f.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        if any(t in data for t in tokens):
            print(f"[acceptance] OK: token match found in {f}")
            return 0

    print(f"[acceptance] FAIL: none of tokens {tokens} found in artifacts under {root}")
    return 3

if __name__ == "__main__":
    sys.exit(main())
