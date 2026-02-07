#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "artifacts" / "stage-1"


REQUIRED_JSON_KEYS = {
    "schema_version",
    "enabled",
    "provider",
    "source",
    "threshold",
    "sample_shape",
}

REQUIRED_SAMPLE_KEYS = {
    "gaze_x",
    "gaze_y",
    "confidence",
    "present",
    "source",
    "timestamp",
}


def main() -> int:
    signal_contract = ARTIFACT_DIR / "signal_contract.md"
    runtime_log = ARTIFACT_DIR / "runtime_validation.log"
    provider_status_path = ARTIFACT_DIR / "provider_status.json"

    for p in [signal_contract, runtime_log, provider_status_path]:
        if not p.exists():
            print(f"FAIL missing {p}")
            return 2

    provider_status = json.loads(provider_status_path.read_text(encoding="utf-8"))

    missing = REQUIRED_JSON_KEYS.difference(provider_status.keys())
    if missing:
        print(f"FAIL provider_status.json missing keys: {sorted(missing)}")
        return 3

    sample_shape = provider_status["sample_shape"]
    if not REQUIRED_SAMPLE_KEYS.issubset(sample_shape.keys()):
        print("FAIL provider_status.json sample_shape missing required schema fields")
        return 4

    log_text = runtime_log.read_text(encoding="utf-8")
    if "gating_pass=" not in log_text or "gating_suppressed=" not in log_text:
        print("FAIL runtime_validation.log missing gating summary")
        return 5

    if "time-series" in log_text.lower():
        print("FAIL runtime_validation.log must not contain raw stream markers")
        return 6

    print("STAGE1_ARTIFACT_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
