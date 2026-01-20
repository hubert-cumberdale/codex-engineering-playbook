from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class ExternalReference:
    source_name: str | None
    url: str | None
    description: str | None
    external_id: str | None

@dataclass(frozen=True)
class TechniqueRef:
    stix_id: str
    external_id: str | None = None

@dataclass(frozen=True)
class AnalyticRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    platforms: tuple[str, ...] = field(default_factory=tuple)
    data_sources: tuple[str, ...] = field(default_factory=tuple)
    technique_refs: tuple[TechniqueRef, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class DetectionStrategyRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    domains: tuple[str, ...] = field(default_factory=tuple)
    platforms: tuple[str, ...] = field(default_factory=tuple)
    data_sources: tuple[str, ...] = field(default_factory=tuple)
    analytics: tuple[AnalyticRecord, ...] = field(default_factory=tuple)
    technique_refs: tuple[TechniqueRef, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)
