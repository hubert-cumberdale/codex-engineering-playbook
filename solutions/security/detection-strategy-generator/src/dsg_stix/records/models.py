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
class LogSourceReference:
    data_component_ref: str | None
    name: str | None
    channel: str | None

@dataclass(frozen=True)
class MutableElement:
    field: str | None
    description: str | None

@dataclass(frozen=True)
class DataSourceRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    platforms: tuple[str, ...] = field(default_factory=tuple)
    domains: tuple[str, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class DataComponentRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    data_source_ref: str | None
    domains: tuple[str, ...] = field(default_factory=tuple)
    log_sources: tuple[str, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class MitigationRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    domains: tuple[str, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class SoftwareRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    software_type: str
    platforms: tuple[str, ...] = field(default_factory=tuple)
    domains: tuple[str, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class AnalyticRecord:
    stix_id: str
    name: str | None
    description: str | None
    external_id: str | None
    platforms: tuple[str, ...] = field(default_factory=tuple)
    data_sources: tuple[str, ...] = field(default_factory=tuple)
    data_source_objects: tuple[DataSourceRecord, ...] = field(default_factory=tuple)
    data_component_objects: tuple[DataComponentRecord, ...] = field(default_factory=tuple)
    mitigations: tuple[MitigationRecord, ...] = field(default_factory=tuple)
    software: tuple[SoftwareRecord, ...] = field(default_factory=tuple)
    log_source_references: tuple[LogSourceReference, ...] = field(default_factory=tuple)
    mutable_elements: tuple[MutableElement, ...] = field(default_factory=tuple)
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
    data_source_objects: tuple[DataSourceRecord, ...] = field(default_factory=tuple)
    data_component_objects: tuple[DataComponentRecord, ...] = field(default_factory=tuple)
    mitigations: tuple[MitigationRecord, ...] = field(default_factory=tuple)
    software: tuple[SoftwareRecord, ...] = field(default_factory=tuple)
    analytics: tuple[AnalyticRecord, ...] = field(default_factory=tuple)
    analytic_ref_objects: tuple[AnalyticRecord, ...] = field(default_factory=tuple)
    analytic_ref_unresolved: tuple[str, ...] = field(default_factory=tuple)
    technique_refs: tuple[TechniqueRef, ...] = field(default_factory=tuple)
    external_references: tuple[ExternalReference, ...] = field(default_factory=tuple)
