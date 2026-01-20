from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

Json = Any
JsonObj = Mapping[str, Any]

@dataclass(frozen=True)
class BundleMeta:
    bundle_id: str | None
    spec_version: str | None
    sha256: str  # computed from raw bytes
    object_count: int

@dataclass(frozen=True)
class StixObject:
    """Opaque STIX object wrapper (no inference)."""
    type: str
    id: str
    raw: dict[str, Any]  # exact JSON object

@dataclass(frozen=True)
class Relationship:
    id: str
    relationship_type: str
    source_ref: str
    target_ref: str
    raw: dict[str, Any]

@dataclass(frozen=True)
class ExtractionResult:
    meta: BundleMeta
    domain: str  # 'enterprise'|'mobile'|'ics' (caller-provided)
    detection_strategies: tuple[StixObject, ...] = field(default_factory=tuple)
    analytics: tuple[StixObject, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)
    techniques: tuple[StixObject, ...] = field(default_factory=tuple)

    # Explicit technique ids only if present via relationships/refs in the bundle
    explicit_technique_external_ids: tuple[str, ...] = field(default_factory=tuple)
