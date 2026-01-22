from __future__ import annotations

from typing import Iterable

from ..models import ExtractionResult, Relationship, StixObject
from .models import (
    AnalyticRecord,
    DataComponentRecord,
    DataSourceRecord,
    DetectionStrategyRecord,
    ExternalReference,
    LogSourceReference,
    MitigationRecord,
    MutableElement,
    SoftwareRecord,
    TechniqueRef,
)

ATTACK_PATTERN_PREFIX = "attack-pattern--"

RELATED_RELATIONSHIP_TYPES = {
    "data_source": ("related-to",),
    "data_component": ("related-to",),
    "mitigation": ("mitigates", "related-to"),
    "software": ("uses", "related-to"),
}

def build_records(extraction: ExtractionResult) -> tuple[DetectionStrategyRecord, ...]:
    technique_external_ids = _build_technique_external_id_map(extraction.techniques)
    data_sources_by_id = {
        source.id: _build_data_source_record(source)
        for source in extraction.data_sources
    }
    data_components_by_id = {
        component.id: _build_data_component_record(component)
        for component in extraction.data_components
    }
    mitigations_by_id = {
        mitigation.id: _build_mitigation_record(mitigation)
        for mitigation in extraction.mitigations
    }
    software_by_id = {
        software.id: _build_software_record(software)
        for software in extraction.software
    }
    analytics_by_id = {
        analytic.id: _build_analytic_record(
            analytic,
            extraction.relationships,
            technique_external_ids,
            data_sources_by_id,
            data_components_by_id,
            mitigations_by_id,
            software_by_id,
        )
        for analytic in extraction.analytics
    }

    records: list[DetectionStrategyRecord] = []
    for ds in extraction.detection_strategies:
        analytic_ids = _collect_related_ids(
            ds.id,
            extraction.relationships,
            set(analytics_by_id.keys()),
            relationship_types=("includes",),
        )
        analytic_ref_ids = _extract_str_list(ds.raw, "x_mitre_analytic_refs")
        analytic_ref_objects, analytic_ref_unresolved = _resolve_analytic_refs(
            analytic_ref_ids,
            analytics_by_id,
        )
        analytics = tuple(sorted(
            (analytics_by_id[aid] for aid in analytic_ids if aid in analytics_by_id),
            key=lambda a: a.stix_id,
        ))
        records.append(DetectionStrategyRecord(
            stix_id=ds.id,
            name=_extract_str(ds.raw, "name"),
            description=_extract_str(ds.raw, "description"),
            external_id=_extract_external_id(ds.raw),
            domains=_extract_str_list(ds.raw, "x_mitre_domains"),
            platforms=_extract_str_list(ds.raw, "x_mitre_platforms"),
            data_sources=_extract_str_list(ds.raw, "x_mitre_data_sources"),
            data_source_objects=_collect_related_records(
                ds.id,
                extraction.relationships,
                data_sources_by_id,
                RELATED_RELATIONSHIP_TYPES["data_source"],
            ),
            data_component_objects=_collect_related_records(
                ds.id,
                extraction.relationships,
                data_components_by_id,
                RELATED_RELATIONSHIP_TYPES["data_component"],
            ),
            mitigations=_collect_related_records(
                ds.id,
                extraction.relationships,
                mitigations_by_id,
                RELATED_RELATIONSHIP_TYPES["mitigation"],
            ),
            software=_collect_related_records(
                ds.id,
                extraction.relationships,
                software_by_id,
                RELATED_RELATIONSHIP_TYPES["software"],
            ),
            analytics=analytics,
            analytic_ref_objects=analytic_ref_objects,
            analytic_ref_unresolved=analytic_ref_unresolved,
            technique_refs=_extract_technique_refs(
                ds.id,
                extraction.relationships,
                technique_external_ids,
            ),
            external_references=_extract_external_references(ds.raw),
        ))

    records.sort(key=lambda r: r.stix_id)
    return tuple(records)

def _build_analytic_record(
    analytic: StixObject,
    relationships: Iterable[Relationship],
    technique_external_ids: dict[str, str],
    data_sources_by_id: dict[str, DataSourceRecord],
    data_components_by_id: dict[str, DataComponentRecord],
    mitigations_by_id: dict[str, MitigationRecord],
    software_by_id: dict[str, SoftwareRecord],
) -> AnalyticRecord:
    return AnalyticRecord(
        stix_id=analytic.id,
        name=_extract_str(analytic.raw, "name"),
        description=_extract_str(analytic.raw, "description"),
        external_id=_extract_external_id(analytic.raw),
        platforms=_extract_str_list(analytic.raw, "x_mitre_platforms"),
        data_sources=_extract_str_list(analytic.raw, "x_mitre_data_sources"),
        data_source_objects=_collect_related_records(
            analytic.id,
            relationships,
            data_sources_by_id,
            RELATED_RELATIONSHIP_TYPES["data_source"],
        ),
        data_component_objects=_collect_related_records(
            analytic.id,
            relationships,
            data_components_by_id,
            RELATED_RELATIONSHIP_TYPES["data_component"],
        ),
        mitigations=_collect_related_records(
            analytic.id,
            relationships,
            mitigations_by_id,
            RELATED_RELATIONSHIP_TYPES["mitigation"],
        ),
        software=_collect_related_records(
            analytic.id,
            relationships,
            software_by_id,
            RELATED_RELATIONSHIP_TYPES["software"],
        ),
        log_source_references=_extract_log_source_references(analytic.raw),
        mutable_elements=_extract_mutable_elements(analytic.raw),
        technique_refs=_extract_technique_refs(
            analytic.id,
            relationships,
            technique_external_ids,
        ),
        external_references=_extract_external_references(analytic.raw),
    )

def _collect_related_records(
    stix_id: str,
    relationships: Iterable[Relationship],
    record_by_id: dict[str, object],
    relationship_types: tuple[str, ...],
) -> tuple:
    related_ids = _collect_related_ids(
        stix_id,
        relationships,
        set(record_by_id.keys()),
        relationship_types=relationship_types,
    )
    records = [record_by_id[rid] for rid in related_ids if rid in record_by_id]
    records.sort(key=lambda r: _sort_key(r))
    return tuple(records)

def _collect_related_ids(
    stix_id: str,
    relationships: Iterable[Relationship],
    allowed_ids: set[str],
    relationship_types: tuple[str, ...] | None = None,
) -> list[str]:
    related: set[str] = set()
    for rel in relationships:
        if relationship_types and rel.relationship_type not in relationship_types:
            continue
        if rel.source_ref == stix_id and rel.target_ref in allowed_ids:
            related.add(rel.target_ref)
        elif rel.target_ref == stix_id and rel.source_ref in allowed_ids:
            related.add(rel.source_ref)
    return sorted(related)

def _extract_str(raw: dict, key: str) -> str | None:
    value = raw.get(key)
    return value if isinstance(value, str) else None

def _extract_str_list(raw: dict, key: str) -> tuple[str, ...]:
    value = raw.get(key, [])
    if not isinstance(value, list):
        return tuple()
    items = tuple(sorted({v for v in value if isinstance(v, str)}))
    return items

def _extract_external_id(raw: dict) -> str | None:
    refs = raw.get("external_references") or []
    if not isinstance(refs, list):
        return None
    external_ids = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        ext = ref.get("external_id")
        if isinstance(ext, str):
            external_ids.append(ext)
    if not external_ids:
        return None
    return sorted(external_ids)[0]

def _extract_external_references(raw: dict) -> tuple[ExternalReference, ...]:
    refs = raw.get("external_references") or []
    if not isinstance(refs, list):
        return tuple()
    out: list[ExternalReference] = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        source_name = ref.get("source_name")
        url = ref.get("url")
        description = ref.get("description")
        external_id = ref.get("external_id")
        out.append(ExternalReference(
            source_name=source_name if isinstance(source_name, str) else None,
            url=url if isinstance(url, str) else None,
            description=description if isinstance(description, str) else None,
            external_id=external_id if isinstance(external_id, str) else None,
        ))
    out.sort(key=lambda r: (
        r.source_name or "",
        r.url or "",
        r.external_id or "",
        r.description or "",
    ))
    return tuple(out)

def _extract_log_source_references(raw: dict) -> tuple[LogSourceReference, ...]:
    refs = raw.get("x_mitre_log_source_references") or []
    if not isinstance(refs, list):
        return tuple()
    out: list[LogSourceReference] = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        data_component_ref = ref.get("x_mitre_data_component_ref")
        name = ref.get("name")
        channel = ref.get("channel")
        out.append(LogSourceReference(
            data_component_ref=data_component_ref if isinstance(data_component_ref, str) else None,
            name=name if isinstance(name, str) else None,
            channel=channel if isinstance(channel, str) else None,
        ))
    out.sort(key=lambda r: (
        r.data_component_ref or "",
        r.name or "",
        r.channel or "",
    ))
    return tuple(out)

def _extract_mutable_elements(raw: dict) -> tuple[MutableElement, ...]:
    elements = raw.get("x_mitre_mutable_elements") or []
    if not isinstance(elements, list):
        return tuple()
    out: list[MutableElement] = []
    for element in elements:
        if not isinstance(element, dict):
            continue
        field = element.get("field")
        description = element.get("description")
        out.append(MutableElement(
            field=field if isinstance(field, str) else None,
            description=description if isinstance(description, str) else None,
        ))
    out.sort(key=lambda e: (
        e.field or "",
        e.description or "",
    ))
    return tuple(out)

def _extract_technique_refs(
    stix_id: str,
    relationships: Iterable[Relationship],
    technique_external_ids: dict[str, str],
) -> tuple[TechniqueRef, ...]:
    technique_ids = set()
    for rel in relationships:
        if rel.source_ref == stix_id and rel.target_ref.startswith(ATTACK_PATTERN_PREFIX):
            technique_ids.add(rel.target_ref)
        elif rel.target_ref == stix_id and rel.source_ref.startswith(ATTACK_PATTERN_PREFIX):
            technique_ids.add(rel.source_ref)
    refs = [
        TechniqueRef(stix_id=tid, external_id=technique_external_ids.get(tid))
        for tid in technique_ids
    ]
    refs.sort(key=lambda r: r.stix_id)
    return tuple(refs)

def _build_technique_external_id_map(
    techniques: Iterable[StixObject],
) -> dict[str, str]:
    out: dict[str, str] = {}
    for technique in techniques:
        external_id = _extract_external_id(technique.raw)
        if external_id:
            out[technique.id] = external_id
    return out

def _resolve_analytic_refs(
    analytic_ref_ids: tuple[str, ...],
    analytics_by_id: dict[str, AnalyticRecord],
) -> tuple[tuple[AnalyticRecord, ...], tuple[str, ...]]:
    if not analytic_ref_ids:
        return tuple(), tuple()
    resolved: list[AnalyticRecord] = []
    unresolved: list[str] = []
    for ref_id in analytic_ref_ids:
        analytic = analytics_by_id.get(ref_id)
        if analytic:
            resolved.append(analytic)
        else:
            unresolved.append(ref_id)
    resolved.sort(key=lambda a: a.stix_id)
    unresolved = sorted(set(unresolved))
    return tuple(resolved), tuple(unresolved)

def _sort_key(record) -> tuple[str, str]:
    external_id = getattr(record, "external_id", None)
    return (
        external_id if isinstance(external_id, str) else "",
        record.stix_id,
    )

def _build_data_source_record(source: StixObject) -> DataSourceRecord:
    return DataSourceRecord(
        stix_id=source.id,
        name=_extract_str(source.raw, "name"),
        description=_extract_str(source.raw, "description"),
        external_id=_extract_external_id(source.raw),
        platforms=_extract_str_list(source.raw, "x_mitre_platforms"),
        domains=_extract_str_list(source.raw, "x_mitre_domains"),
        external_references=_extract_external_references(source.raw),
    )

def _build_data_component_record(component: StixObject) -> DataComponentRecord:
    data_source_ref = component.raw.get("x_mitre_data_source_ref")
    return DataComponentRecord(
        stix_id=component.id,
        name=_extract_str(component.raw, "name"),
        description=_extract_str(component.raw, "description"),
        external_id=_extract_external_id(component.raw),
        data_source_ref=data_source_ref if isinstance(data_source_ref, str) else None,
        domains=_extract_str_list(component.raw, "x_mitre_domains"),
        log_sources=_extract_str_list(component.raw, "x_mitre_log_sources"),
        external_references=_extract_external_references(component.raw),
    )

def _build_mitigation_record(mitigation: StixObject) -> MitigationRecord:
    return MitigationRecord(
        stix_id=mitigation.id,
        name=_extract_str(mitigation.raw, "name"),
        description=_extract_str(mitigation.raw, "description"),
        external_id=_extract_external_id(mitigation.raw),
        domains=_extract_str_list(mitigation.raw, "x_mitre_domains"),
        external_references=_extract_external_references(mitigation.raw),
    )

def _build_software_record(software: StixObject) -> SoftwareRecord:
    return SoftwareRecord(
        stix_id=software.id,
        name=_extract_str(software.raw, "name"),
        description=_extract_str(software.raw, "description"),
        external_id=_extract_external_id(software.raw),
        software_type=software.type,
        platforms=_extract_str_list(software.raw, "x_mitre_platforms"),
        domains=_extract_str_list(software.raw, "x_mitre_domains"),
        external_references=_extract_external_references(software.raw),
    )
