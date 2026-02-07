#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
UNREAL_ROOT = ROOT / "Unreal" / "fps-gaze-prototype" / "Source"

DISALLOWED_STAGE_TOKENS = [
    "AimIntentTarget",
    "InteractIntentTarget",
    "UIFocusZone",
    "AimAssist",
    "InteractionAdapter",
    "CameraAdapter",
    "Arena.umap",
]

GAMEPLAY_FORBIDDEN_TOBII = [
    "tobii",
    "itobiicore",
    "tobii_api",
]


def _scan_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    failures: list[str] = []

    if not UNREAL_ROOT.exists():
        print(f"FAIL missing expected source root: {UNREAL_ROOT}")
        return 2

    source_files = [p for p in UNREAL_ROOT.rglob("*") if p.suffix.lower() in {".h", ".hpp", ".cpp", ".cs"}]
    for p in source_files:
        data = _scan_text(p)
        for tok in DISALLOWED_STAGE_TOKENS:
            if tok in data:
                failures.append(f"stage-boundary token '{tok}' in {p}")

    gameplay_module = UNREAL_ROOT / "FPSGazePrototype"
    if gameplay_module.exists():
        gameplay_files = [p for p in gameplay_module.rglob("*") if p.suffix.lower() in {".h", ".hpp", ".cpp"}]
        for p in gameplay_files:
            data = _scan_text(p).lower()
            for tok in GAMEPLAY_FORBIDDEN_TOBII:
                if tok in data:
                    failures.append(f"gameplay sdk token '{tok}' in {p}")

    # Stage-1 boundary: disallow Content/ and Maps/ modifications.
    diff_out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    ).stdout
    for changed in [line.strip() for line in diff_out.splitlines() if line.strip()]:
        if changed.startswith("solutions/game/fps-gaze-prototype/Unreal/fps-gaze-prototype/Content/"):
            failures.append(f"content change outside Stage-1 scope: {changed}")
        if "/Maps/" in changed:
            failures.append(f"maps change outside Stage-1 scope: {changed}")

    if failures:
        print("FAIL stage-1 boundary check")
        for entry in failures:
            print(f" - {entry}")
        return 3

    print("STAGE1_BOUNDARY_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
