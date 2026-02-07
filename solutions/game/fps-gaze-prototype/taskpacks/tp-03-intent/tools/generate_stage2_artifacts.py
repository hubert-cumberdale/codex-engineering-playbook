#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / "taskpacks" / "tp-03-intent" / "fixtures" / "intent_resolution_fixtures.json"
STAGE1_PROVIDER_STATUS_PATH = ROOT / "artifacts" / "stage-1" / "provider_status.json"
ARTIFACT_DIR = ROOT / "artifacts" / "stage-2"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _normalized_fixture_sha256(fixture: dict) -> str:
    canonical = dict(fixture)
    canonical["fixtures_sha256"] = ""
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _prefixed_sha256(hex_digest: str) -> str:
    return f"sha256:{hex_digest}"


def _collect_dot_paths(value: object, prefix: str = "") -> set[str]:
    paths: set[str] = set()

    if isinstance(value, dict):
        for key in sorted(value.keys()):
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            paths.update(_collect_dot_paths(value[key], next_prefix))
        return paths

    if isinstance(value, list):
        array_prefix = f"{prefix}[]"
        if not value:
            paths.add(array_prefix)
            return paths
        for item in value:
            paths.update(_collect_dot_paths(item, array_prefix))
        return paths

    if prefix:
        paths.add(prefix)
    return paths


def _fingerprint_from_paths(paths: set[str]) -> str:
    payload = "\n".join(sorted(paths))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stage1_snapshot_schema_fingerprint() -> str:
    data = json.loads(STAGE1_PROVIDER_STATUS_PATH.read_text(encoding="utf-8"))
    snapshot = data.get("representative_gated_sample")
    if not isinstance(snapshot, dict):
        raise ValueError("Stage-1 provider_status.json missing representative_gated_sample object")
    return _prefixed_sha256(_fingerprint_from_paths(_collect_dot_paths(snapshot)))


def _in_rect(x: float, y: float, rect: dict) -> bool:
    return rect["min_x"] <= x <= rect["max_x"] and rect["min_y"] <= y <= rect["max_y"]


def _priority_key(entry: dict) -> tuple[int, str]:
    return (-int(entry["priority"]), str(entry["id"]))


def _resolve_case(case: dict, scene: dict, threshold_default: float) -> dict:
    threshold = threshold_default
    enabled = bool(case.get("enabled", False))
    provider_kind = str(case.get("provider_kind", "Null"))

    snapshot = case["stage1_provider_snapshot"]
    present = bool(case["present"]) if "present" in case else bool(snapshot["present"])
    confidence = float(snapshot["confidence"])

    suppressed_reason = None
    if not enabled:
        suppressed_reason = "suppressed_disabled"
    elif provider_kind == "Null":
        suppressed_reason = "suppressed_provider_null"
    elif not present:
        suppressed_reason = "suppressed_not_present"
    elif confidence < threshold:
        suppressed_reason = "suppressed_low_confidence"

    if suppressed_reason is not None:
        return {
            "gating": "suppressed",
            "aim_intent_target_id": None,
            "interact_intent_target_id": None,
            "ui_focus_zone_id": None,
            "reason_code": suppressed_reason,
            "tie_break": "suppressed",
        }

    x = float(snapshot["gaze_x"])
    y = float(snapshot["gaze_y"])

    candidates = [target for target in scene["targets"] if _in_rect(x, y, target["screen_region"])]
    aim_candidates = [c for c in candidates if "aimable" in c.get("types", [])]
    interact_candidates = [c for c in candidates if ("interactable" in c.get("types", []) or "ui" in c.get("types", []))]

    aim_target = sorted(aim_candidates, key=_priority_key)[0]["id"] if aim_candidates else None
    interact_target = sorted(interact_candidates, key=_priority_key)[0]["id"] if interact_candidates else None

    ui_focus_zone_id = None
    for zone in scene["ui_zones"]:
        if _in_rect(x, y, zone["screen_region"]):
            ui_focus_zone_id = zone["name"]
            break

    # Stage-2 invariant: UI focus takes precedence and suppresses aim/interact outputs.
    if ui_focus_zone_id is not None:
        aim_target = None
        interact_target = None

    reason_code = "resolved"
    if aim_target is None and interact_target is None and ui_focus_zone_id is None:
        reason_code = "no_candidate"

    return {
        "gating": "pass",
        "aim_intent_target_id": aim_target,
        "interact_intent_target_id": interact_target,
        "ui_focus_zone_id": ui_focus_zone_id,
        "reason_code": reason_code,
        "tie_break": "priority_desc_id_asc",
    }


def main() -> int:
    fixture = _load_fixture()
    declared_fixtures_sha256 = fixture.get("fixtures_sha256")
    computed_fixtures_sha256 = _prefixed_sha256(_normalized_fixture_sha256(fixture))
    if not isinstance(declared_fixtures_sha256, str):
        raise ValueError("fixture must include string fixtures_sha256")
    if declared_fixtures_sha256 != computed_fixtures_sha256:
        raise ValueError(
            "fixture fixtures_sha256 mismatch: "
            f"declared={declared_fixtures_sha256} computed={computed_fixtures_sha256}"
        )

    fixtures_sha256 = declared_fixtures_sha256
    schema_fingerprint = _stage1_snapshot_schema_fingerprint()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    scene = fixture["scene"]
    resolver_config = fixture["resolver_config"]
    threshold_default = float(int(resolver_config["confidence_min_q"])) / 100.0

    rows: list[dict] = []
    failures: list[str] = []

    cases = sorted(fixture["cases"], key=lambda x: str(x["case_id"]))

    for case in cases:
        resolved = _resolve_case(case, scene, threshold_default)
        expected = case["expect"]
        matched = (
            resolved["aim_intent_target_id"] == expected["aim_intent_target_id"]
            and resolved["interact_intent_target_id"] == expected["interact_intent_target_id"]
            and resolved["ui_focus_zone_id"] == expected["ui_focus_zone_id"]
            and resolved["reason_code"] == expected["reason_code"]
            and resolved["tie_break"] == expected["tie_break"]
        )
        if not matched:
            failures.append(str(case["case_id"]))

        rows.append(
            {
                "case_id": str(case["case_id"]),
                "gating": resolved["gating"],
                "aim_intent_target_id": resolved["aim_intent_target_id"],
                "interact_intent_target_id": resolved["interact_intent_target_id"],
                "ui_focus_zone_id": resolved["ui_focus_zone_id"],
                "reason_code": resolved["reason_code"],
                "tie_break": resolved["tie_break"],
                "expected_match": matched,
            }
        )

    report = {
        "schema_version": str(fixture["schema_version"]),
        "stage": "stage-2",
        "deterministic": True,
        "inputs": {
            "fixtures_sha256": fixtures_sha256,
        },
        "fixtures_sha256": fixtures_sha256,
        "stage1_snapshot_schema_fingerprint": schema_fingerprint,
        "resolution_rules": {
            "input_gating": "enabled && provider_kind!=Null && present && confidence>=threshold",
            "tie_break": "priority_desc_then_id_asc",
            "null_intent_on_suppression": True,
        },
        "scene_summary": {
            "target_ids": sorted(t["id"] for t in scene["targets"]),
            "ui_zone_names": [z["name"] for z in scene["ui_zones"]],
        },
        "case_count": len(rows),
        "rows": rows,
        "all_expected_matched": len(failures) == 0,
    }

    log_lines = [
        "stage-2 intent_resolution deterministic",
        f"fixture={FIXTURE_PATH.as_posix()}",
        "tie_break=priority_desc_then_id_asc",
        "null_intent=true",
    ]

    for row in rows:
        log_lines.append(
            "case={id} gating={gating} aim={aim} interact={interact} ui_focus={ui} reason_code={reason} expected_match={match}".format(
                id=row["case_id"],
                gating=row["gating"],
                aim=row["aim_intent_target_id"] if row["aim_intent_target_id"] is not None else "null",
                interact=row["interact_intent_target_id"] if row["interact_intent_target_id"] is not None else "null",
                ui=row["ui_focus_zone_id"] if row["ui_focus_zone_id"] is not None else "null",
                reason=row["reason_code"],
                match=str(row["expected_match"]).lower(),
            )
        )

    joined_log = "\n".join(log_lines) + "\n"
    prohibited = ["gaze_x=", "gaze_y=", "samples[", "time_series", "raw"]
    lowered = joined_log.lower()
    for token in prohibited:
        if token in lowered:
            raise ValueError(f"intent_resolution.log contains prohibited token: {token}")

    if failures:
        raise ValueError(f"fixture expected output mismatch for cases: {', '.join(failures)}")

    (ARTIFACT_DIR / "intent_resolution.log").write_text(joined_log, encoding="utf-8")
    (ARTIFACT_DIR / "intent_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("STAGE2_ARTIFACTS_WRITTEN")
    print(str(ARTIFACT_DIR / "intent_resolution.log"))
    print(str(ARTIFACT_DIR / "intent_report.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
