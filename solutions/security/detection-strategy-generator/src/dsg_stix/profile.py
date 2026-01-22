from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

UNKNOWN_PROFILE = "Not provided by source"

@dataclass(frozen=True)
class ProfileOverlay:
    profile_id: str
    profile_hash: str
    priority_default: str | None
    priority_by_stix_id: dict[str, str]
    priority_by_external_id: dict[str, str]
    applicability_by_stix_id: dict[str, str]
    applicability_by_external_id: dict[str, str]
    validation_by_stix_id: dict[str, str]
    validation_by_external_id: dict[str, str]

def load_profile(path: Path) -> ProfileOverlay:
    raw_bytes = path.read_bytes()
    raw = json.loads(raw_bytes)
    if not isinstance(raw, dict):
        raise ValueError("Profile must be a JSON object.")
    profile_id = raw.get("profile_id")
    if not isinstance(profile_id, str):
        profile_id = UNKNOWN_PROFILE

    priority_default, priority_by_stix_id, priority_by_external_id = _load_section(
        raw, "priority"
    )
    _, applicability_by_stix_id, applicability_by_external_id = _load_section(
        raw, "applicability"
    )
    _, validation_by_stix_id, validation_by_external_id = _load_section(
        raw, "validation_status"
    )

    return ProfileOverlay(
        profile_id=profile_id,
        profile_hash=_sha256_hex(raw_bytes),
        priority_default=priority_default,
        priority_by_stix_id=priority_by_stix_id,
        priority_by_external_id=priority_by_external_id,
        applicability_by_stix_id=applicability_by_stix_id,
        applicability_by_external_id=applicability_by_external_id,
        validation_by_stix_id=validation_by_stix_id,
        validation_by_external_id=validation_by_external_id,
    )

def _load_section(
    raw: Mapping[str, Any],
    key: str,
) -> tuple[str | None, dict[str, str], dict[str, str]]:
    section = raw.get(key, {})
    if not isinstance(section, dict):
        return None, {}, {}
    default_value = section.get("default")
    if not isinstance(default_value, str):
        default_value = None
    by_stix_id = _extract_str_map(section.get("by_stix_id", {}))
    by_external_id = _extract_str_map(section.get("by_external_id", {}))
    return default_value, by_stix_id, by_external_id

def _extract_str_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for key, val in value.items():
        if isinstance(key, str) and isinstance(val, str):
            out[key] = val
    return out

def _sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
