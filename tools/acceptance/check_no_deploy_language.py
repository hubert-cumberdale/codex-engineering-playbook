#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

FORBIDDEN = [
    "kubectl apply",
    "terraform apply",
    "helm install",
    "aws deploy",
    "deploy to production",
    "apply to cluster",
]

SKIP_DIRS = {".git", ".orchestrator_logs", ".venv", "node_modules", "dist", "build", "__pycache__", "tools/acceptance"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Root to scan")
    args = ap.parse_args()

    root = Path(args.path)
    hits = []

    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".yml", ".yaml", ".sh", ".ps1", ".py", ".js", ".ts"}:
            if p.samefile(Path(__file__)):
                continue

            data = p.read_text(encoding="utf-8", errors="ignore").lower()
            for pat in FORBIDDEN:
                if pat in data:
                    hits.append((str(p), pat))

    if hits:
        print("[acceptance] FAIL: deployment language detected:")
        for f, pat in hits[:50]:
            print(f" - {f}: {pat}")
        return 2

    print("[acceptance] OK: no deployment language detected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
