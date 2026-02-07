#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / "taskpacks" / "tp-02-provider" / "fixtures" / "validation_inputs.json"
ARTIFACT_DIR = ROOT / "artifacts" / "stage-1"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _gated_sample(sample: dict, threshold: float, source: str) -> tuple[dict, bool]:
    if source == "Null":
        return (
            {
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "present": False,
                "source": source,
                "timestamp": float(sample["timestamp"]),
            },
            False,
        )

    passed = bool(sample.get("present", False)) and float(sample.get("confidence", 0.0)) >= threshold
    if not passed:
        return (
            {
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "present": False,
                "source": source,
                "timestamp": float(sample["timestamp"]),
            },
            False,
        )

    return (
        {
            "gaze_x": _clamp01(float(sample["gaze_x"])),
            "gaze_y": _clamp01(float(sample["gaze_y"])),
            "confidence": _clamp01(float(sample["confidence"])),
            "present": True,
            "source": source,
            "timestamp": float(sample["timestamp"]),
        },
        True,
    )


def _write_signal_contract(path: Path) -> None:
    content = """# Stage-1 Normalized Signal Contract

- Coordinate space: screen-space normalized viewport with origin at top-left.
- Timestamp: monotonic seconds from engine monotonic clock.
- No raw gaze stream persistence.

## Fields
- `gaze_x`: float in `[0.0, 1.0]`.
- `gaze_y`: float in `[0.0, 1.0]`.
- `confidence`: float in `[0.0, 1.0]`.
- `present`: bool indicating whether gaze is valid after confidence gating.
- `source`: enum string `Tobii|Null`.
- `timestamp`: monotonic numeric value; not wall-clock.

## Gating Rule
- Threshold is `0.60`.
- If `confidence < threshold` or sample is not present, output is explicit no-gaze.
- Gated output shape is deterministic and does not include time-series history.
"""
    path.write_text(content, encoding="utf-8")


def main() -> int:
    fixture = _load_fixture()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    threshold = float(fixture["threshold"])
    requested_provider = str(fixture["provider"])
    provider_available = bool(fixture["provider_available"])
    enabled = bool(fixture["enabled"])
    active_source = requested_provider if enabled and provider_available and requested_provider == "Tobii" else "Null"

    gating_pass = 0
    gating_suppressed = 0
    representative = None

    for sample in fixture["samples"]:
        gated, passed = _gated_sample(sample, threshold, active_source)
        if passed:
            gating_pass += 1
        else:
            gating_suppressed += 1
        if representative is None:
            representative = gated

    provider_status = {
        "schema_version": str(fixture["schema_version"]),
        "enabled": enabled,
        "provider": requested_provider,
        "source": active_source,
        "threshold": threshold,
        "sample_shape": {
            "gaze_x": "float(0..1)",
            "gaze_y": "float(0..1)",
            "confidence": "float(0..1)",
            "present": "bool",
            "source": "enum(Tobii|Null)",
            "timestamp": "monotonic"
        },
        "representative_gated_sample": representative,
    }

    # Mechanical guard: Stage-1 artifact is a schema + single snapshot only.
    if isinstance(provider_status.get("representative_gated_sample"), list):
        raise ValueError("provider_status.json must contain a single sample object, not an array")
    if "samples" in provider_status:
        raise ValueError("provider_status.json must not contain sample history arrays")

    runtime_log = "\n".join(
        [
            "STAGE1_VALIDATION deterministic",
            f"enabled={str(enabled).lower()}",
            f"provider_requested={requested_provider}",
            f"provider_available={str(provider_available).lower()}",
            f"provider_active={active_source}",
            f"threshold={threshold:.2f}",
            f"gating_pass={gating_pass}",
            f"gating_suppressed={gating_suppressed}",
            "timestamp_semantics=monotonic",
        ]
    ) + "\n"

    # Mechanical guard: log summary must not emit repeated raw gaze coordinates.
    if "gaze_x=" in runtime_log or "gaze_y=" in runtime_log:
        raise ValueError("runtime_validation.log must not contain raw gaze coordinates")

    _write_signal_contract(ARTIFACT_DIR / "signal_contract.md")
    (ARTIFACT_DIR / "runtime_validation.log").write_text(runtime_log, encoding="utf-8")
    (ARTIFACT_DIR / "provider_status.json").write_text(
        json.dumps(provider_status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("STAGE1_ARTIFACTS_WRITTEN")
    print(str(ARTIFACT_DIR / "signal_contract.md"))
    print(str(ARTIFACT_DIR / "runtime_validation.log"))
    print(str(ARTIFACT_DIR / "provider_status.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
