from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .errors import StixFormatError
from .models import BundleMeta

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def load_bundle_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    data = path.read_bytes()
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception as e:
        raise StixFormatError(f"Invalid JSON: {e}") from e
    if not isinstance(obj, dict):
        raise StixFormatError("STIX bundle must be a JSON object.")
    if obj.get("type") != "bundle":
        raise StixFormatError("STIX root must have type='bundle'.")
    if "objects" not in obj or not isinstance(obj["objects"], list):
        raise StixFormatError("STIX bundle must contain an 'objects' array.")
    return data, obj

def bundle_meta(bundle_bytes: bytes, bundle_obj: dict[str, Any]) -> BundleMeta:
    return BundleMeta(
        bundle_id=bundle_obj.get("id"),
        spec_version=bundle_obj.get("spec_version"),
        sha256=sha256_bytes(bundle_bytes),
        object_count=len(bundle_obj.get("objects", [])),
    )
