#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "artifacts" / "stage-2"
FIXTURE_PATH = ROOT / "taskpacks" / "tp-03-intent" / "fixtures" / "intent_resolution_fixtures.json"

REQUIRED_REPORT_KEYS = {
    "schema_version",
    "stage",
    "deterministic",
    "inputs",
    "fixtures_sha256",
    "stage1_snapshot_schema_fingerprint",
    "resolution_rules",
    "scene_summary",
    "case_count",
    "rows",
    "all_expected_matched",
}

REQUIRED_ROW_KEYS = {
    "case_id",
    "gating",
    "aim_intent_target_id",
    "interact_intent_target_id",
    "ui_focus_zone_id",
    "reason_code",
    "tie_break",
    "expected_match",
}

REQUIRED_LOG_KEYWORDS = ["stage-2", "deterministic", "tie_break", "null_intent"]
PROHIBITED_LOG_PATTERNS = ["gaze_x=", "gaze_y=", "samples[", "time_series", "raw"]


def _normalized_fixture_sha256(fixture: dict) -> str:
    canonical = dict(fixture)
    canonical["fixtures_sha256"] = ""
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _prefixed_sha256(hex_digest: str) -> str:
    return f"sha256:{hex_digest}"


def main() -> int:
    intent_log = ARTIFACT_DIR / "intent_resolution.log"
    intent_report_path = ARTIFACT_DIR / "intent_report.json"

    for p in [intent_log, intent_report_path]:
        if not p.exists():
            print(f"FAIL missing {p}")
            return 2

    report = json.loads(intent_report_path.read_text(encoding="utf-8"))
    missing = REQUIRED_REPORT_KEYS.difference(report.keys())
    if missing:
        print(f"FAIL intent_report.json missing keys: {sorted(missing)}")
        return 3

    rows = report["rows"]
    if not isinstance(rows, list) or not rows:
        print("FAIL intent_report.json rows must be a non-empty list")
        return 4

    for idx, row in enumerate(rows):
        if not REQUIRED_ROW_KEYS.issubset(row.keys()):
            print(f"FAIL row {idx} missing required keys")
            return 5

    if int(report["case_count"]) != len(rows):
        print("FAIL case_count does not match rows length")
        return 6

    if not bool(report["deterministic"]):
        print("FAIL report must declare deterministic=true")
        return 7

    if not isinstance(report["fixtures_sha256"], str) or re.fullmatch(r"sha256:[0-9a-f]{64}", report["fixtures_sha256"]) is None:
        print("FAIL fixtures_sha256 must be sha256:<64-lowercase-hex>")
        return 8

    if not isinstance(report["inputs"], dict):
        print("FAIL report inputs must be an object")
        return 8
    if report["inputs"].get("fixtures_sha256") != report["fixtures_sha256"]:
        print("FAIL report inputs.fixtures_sha256 must match report fixtures_sha256")
        return 8

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture_declared_sha = fixture.get("fixtures_sha256")
    fixture_computed_sha = _prefixed_sha256(_normalized_fixture_sha256(fixture))
    if fixture_declared_sha != fixture_computed_sha:
        print(
            "FAIL fixture fixtures_sha256 mismatch "
            f"declared={fixture_declared_sha} computed={fixture_computed_sha}"
        )
        return 8
    if report["inputs"]["fixtures_sha256"] != fixture_declared_sha:
        print("FAIL report inputs.fixtures_sha256 does not match fixtures file fixtures_sha256")
        return 8

    if not isinstance(report["stage1_snapshot_schema_fingerprint"], str) or re.fullmatch(r"sha256:[0-9a-f]{64}", report["stage1_snapshot_schema_fingerprint"]) is None:
        print("FAIL stage1_snapshot_schema_fingerprint must be sha256:<64-lowercase-hex>")
        return 9

    log_text = intent_log.read_text(encoding="utf-8")
    lowered = log_text.lower()

    for keyword in REQUIRED_LOG_KEYWORDS:
        if keyword not in lowered:
            print(f"FAIL intent_resolution.log missing keyword: {keyword}")
            return 10

    for token in PROHIBITED_LOG_PATTERNS:
        if token in lowered:
            print(f"FAIL intent_resolution.log contains prohibited token: {token}")
            return 11

    print("STAGE2_ARTIFACT_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
