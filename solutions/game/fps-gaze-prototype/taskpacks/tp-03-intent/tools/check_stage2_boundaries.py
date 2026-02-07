#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
UNREAL_ROOT = ROOT / "Unreal" / "fps-gaze-prototype" / "Source"
FIXTURE_PATH = ROOT / "taskpacks" / "tp-03-intent" / "fixtures" / "intent_resolution_fixtures.json"
STAGE1_PROVIDER_STATUS_PATH = ROOT / "artifacts" / "stage-1" / "provider_status.json"

FORBIDDEN_STAGE34_TOKENS = [
    "AimAssist",
    "ExtendedView",
    "CleanUI",
    "InteractionAdapter",
    "CameraAdapter",
    "UIAdapter",
    "InteractHighlight",
    "Arena.umap",
]

FORBIDDEN_STAGE_CREEP_TERMS = [
    "smoothing",
    "hysteresis",
    "dwell",
    "history",
    "time_series",
    "timeseries",
]

FORBIDDEN_GAMEPLAY_EFFECT_CALLS = [
    "applydamage(",
    "setactorlocation(",
    "setcontrolrotation(",
    "addcontrollerpitchinput(",
    "addcontrolleryawinput(",
    "launchcharacter(",
]

FORBIDDEN_ADAPTER_PATTERN = re.compile(r"\b[A-Za-z0-9_]*Adapter\b")


def _scan_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


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


def _normalized_fixture_sha256(fixture: dict) -> str:
    canonical = dict(fixture)
    canonical["fixtures_sha256"] = ""
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _prefixed_sha256(hex_digest: str) -> str:
    return f"sha256:{hex_digest}"


def _load_stage1_snapshot() -> tuple[dict, set[str], str]:
    if not STAGE1_PROVIDER_STATUS_PATH.exists():
        raise ValueError(f"missing Stage-1 artifact: {STAGE1_PROVIDER_STATUS_PATH}")

    data = json.loads(STAGE1_PROVIDER_STATUS_PATH.read_text(encoding="utf-8"))

    snapshot = data.get("representative_gated_sample")
    if not isinstance(snapshot, dict):
        raise ValueError("Stage-1 provider_status.json missing object 'representative_gated_sample'")

    expected_keys = {"gaze_x", "gaze_y", "confidence", "present", "source", "timestamp"}
    if set(snapshot.keys()) != expected_keys:
        raise ValueError(
            "Stage-1 representative_gated_sample keys mismatch: "
            f"expected={sorted(expected_keys)} actual={sorted(snapshot.keys())}"
        )

    def _is_snapshot_object(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        if set(value.keys()) != expected_keys:
            return False
        if not isinstance(value["present"], bool):
            return False
        if not isinstance(value["source"], str):
            return False
        numeric_keys = ("gaze_x", "gaze_y", "confidence", "timestamp")
        return all(isinstance(value[k], (int, float)) for k in numeric_keys)

    sample_like_count = sum(1 for value in data.values() if _is_snapshot_object(value))
    if sample_like_count != 1:
        raise ValueError(
            "Stage-1 provider_status.json must contain exactly one snapshot object "
            f"with keys {sorted(expected_keys)}; found {sample_like_count}"
        )

    paths = _collect_dot_paths(snapshot)
    return snapshot, paths, _fingerprint_from_paths(paths)


def main() -> int:
    failures: list[str] = []

    try:
        _, canonical_paths, canonical_fingerprint = _load_stage1_snapshot()
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL stage-2 boundary check: {exc}")
        return 2

    if not FIXTURE_PATH.exists():
        print(f"FAIL stage-2 boundary check: missing fixture {FIXTURE_PATH}")
        return 2

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "stage2.intent_resolution_fixtures.v1":
        print("FAIL stage-2 boundary check: fixture schema_version must be stage2.intent_resolution_fixtures.v1")
        return 2

    declared_fixtures_sha256 = fixture.get("fixtures_sha256")
    if not isinstance(declared_fixtures_sha256, str):
        print("FAIL stage-2 boundary check: fixture must define string fixtures_sha256")
        return 2
    if re.fullmatch(r"sha256:[0-9a-f]{64}", declared_fixtures_sha256) is None:
        print("FAIL stage-2 boundary check: fixtures_sha256 must be sha256:<64-lowercase-hex>")
        return 2
    computed_fixtures_sha256 = _prefixed_sha256(_normalized_fixture_sha256(fixture))
    if declared_fixtures_sha256 != computed_fixtures_sha256:
        print("FAIL stage-2 boundary check: fixtures_sha256 mismatch")
        print(f"expected hash: {declared_fixtures_sha256}")
        print(f"computed hash: {computed_fixtures_sha256}")
        print(f"fixture path: {FIXTURE_PATH}")
        return 2

    if "threshold_default" in fixture:
        print("FAIL stage-2 boundary check: threshold_default is not allowed; use resolver_config.confidence_min_q")
        return 2

    resolver_config = fixture.get("resolver_config")
    if not isinstance(resolver_config, dict) or "confidence_min_q" not in resolver_config:
        print("FAIL stage-2 boundary check: fixture must define resolver_config.confidence_min_q")
        return 2
    if not isinstance(resolver_config["confidence_min_q"], int):
        print("FAIL stage-2 boundary check: resolver_config.confidence_min_q must be int")
        return 2

    cases = fixture.get("cases")
    if not isinstance(cases, list) or not cases:
        print("FAIL stage-2 boundary check: fixture must contain non-empty 'cases' list")
        return 2

    for case in cases:
        case_id = str(case.get("case_id", "<missing-case-id>"))
        if "threshold" in case:
            failures.append(f"case '{case_id}' must not define threshold; use resolver_config.confidence_min_q")

        if "stage1_provider_snapshot" not in case:
            failures.append(f"case '{case_id}' missing stage1_provider_snapshot")
            continue

        snapshot = case["stage1_provider_snapshot"]
        if not isinstance(snapshot, dict):
            failures.append(f"case '{case_id}' stage1_provider_snapshot must be an object")
            continue

        case_paths = _collect_dot_paths(snapshot)
        case_fingerprint = _fingerprint_from_paths(case_paths)
        if case_fingerprint != canonical_fingerprint:
            missing_paths = sorted(canonical_paths.difference(case_paths))
            extra_paths = sorted(case_paths.difference(canonical_paths))
            failures.append(
                "case '{case_id}' stage1_provider_snapshot schema mismatch: "
                "expected_fingerprint={expected} actual_fingerprint={actual} "
                "missing_paths={missing} extra_paths={extra}".format(
                    case_id=case_id,
                    expected=canonical_fingerprint,
                    actual=case_fingerprint,
                    missing=missing_paths,
                    extra=extra_paths,
                )
            )

        if "expected" in case:
            failures.append(f"case '{case_id}' must use 'expect' instead of 'expected'")
        expect = case.get("expect")
        if not isinstance(expect, dict):
            failures.append(f"case '{case_id}' missing expect object")
            continue
        required_expect_keys = {
            "aim_intent_target_id",
            "interact_intent_target_id",
            "ui_focus_zone_id",
            "reason_code",
            "tie_break",
        }
        missing_expect = sorted(required_expect_keys.difference(expect.keys()))
        if missing_expect:
            failures.append(f"case '{case_id}' expect missing keys: {missing_expect}")
            continue

        if expect["ui_focus_zone_id"] is not None:
            if expect["aim_intent_target_id"] is not None or expect["interact_intent_target_id"] is not None:
                failures.append(
                    f"case '{case_id}' violates ui precedence: ui_focus_zone_id non-null requires aim/interact null"
                )

    if not UNREAL_ROOT.exists():
        print(f"FAIL missing expected source root: {UNREAL_ROOT}")
        return 2

    source_files = [p for p in UNREAL_ROOT.rglob("*") if p.suffix.lower() in {".h", ".hpp", ".cpp", ".cs"}]
    for p in source_files:
        data = _scan_text(p)
        lowered = data.lower()

        for tok in FORBIDDEN_STAGE34_TOKENS:
            if tok in data:
                failures.append(f"forbidden stage-3/4 token '{tok}' in {p}")

        for tok in FORBIDDEN_STAGE_CREEP_TERMS:
            if tok in lowered:
                failures.append(f"forbidden stage-creep term '{tok}' in {p}")

        for tok in FORBIDDEN_GAMEPLAY_EFFECT_CALLS:
            if tok in lowered:
                failures.append(f"forbidden gameplay effect call '{tok}' in {p}")

        if FORBIDDEN_ADAPTER_PATTERN.search(data):
            failures.append(f"forbidden adapter naming in {p}")

    diff_out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    ).stdout

    for changed in [line.strip() for line in diff_out.splitlines() if line.strip()]:
        if changed.startswith("solutions/game/fps-gaze-prototype/Unreal/fps-gaze-prototype/Content/"):
            failures.append(f"content change outside Stage-2 scope: {changed}")
        if "/Maps/" in changed or changed.endswith(".umap"):
            failures.append(f"maps change outside Stage-2 scope: {changed}")

    if failures:
        print("FAIL stage-2 boundary check")
        for entry in failures:
            print(f" - {entry}")
        return 3

    print("STAGE2_BOUNDARY_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
