from __future__ import annotations

from typing import Iterable

from ..models import ExtractionResult, Relationship, StixObject
from .models import (
    AnalyticRecord,
    DetectionStrategyRecord,
    ExternalReference,
    TechniqueRef,
)

ATTACK_PATTERN_PREFIX = "attack-pattern--"

def build_records(extraction: ExtractionResult) -> tuple[DetectionStrategyRecord, ...]:
    technique_external_ids = _build_technique_external_id_map(extraction.techniques)
    analytics_by_id = {
        analytic.id: _build_analytic_record(
            analytic,
            extraction.relationships,
            technique_external_ids,
        )
        for analytic in extraction.analytics
    }

    records: list[DetectionStrategyRecord] = []
    for ds in extraction.detection_strategies:
        analytic_ids = [
            rel.target_ref
            for rel in extraction.relationships
            if rel.relationship_type == "includes" and rel.source_ref == ds.id
        ]
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
            analytics=analytics,
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
) -> AnalyticRecord:
    return AnalyticRecord(
        stix_id=analytic.id,
        name=_extract_str(analytic.raw, "name"),
        description=_extract_str(analytic.raw, "description"),
        external_id=_extract_external_id(analytic.raw),
        platforms=_extract_str_list(analytic.raw, "x_mitre_platforms"),
        data_sources=_extract_str_list(analytic.raw, "x_mitre_data_sources"),
        technique_refs=_extract_technique_refs(
            analytic.id,
            relationships,
            technique_external_ids,
        ),
        external_references=_extract_external_references(analytic.raw),
    )

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
