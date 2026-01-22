from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from ..models import ExtractionResult
from ..records.models import (
    DetectionStrategyRecord,
    ExternalReference,
    TechniqueRef,
)
from ..profile import ProfileOverlay
from .constants import GENERATOR_VERSION, UNKNOWN

SECTION_HEADERS = (
    "Goal",
    "Categorization",
    "Strategy Abstract",
    "Technical Context",
    "Blind Spots and Assumptions",
    "False Positives",
    "Validation",
    "Priority",
    "Response",
    "Additional Resources",
)

@dataclass(frozen=True)
class RenderConfig:
    render_timestamp: str
    generator_version: str = GENERATOR_VERSION
    company_profile_id: str = UNKNOWN
    company_profile_hash: str = UNKNOWN
    profile: ProfileOverlay | None = None

def render_detection_strategy(
    record: DetectionStrategyRecord,
    extraction: ExtractionResult,
    config: RenderConfig,
) -> str:
    _validate_timestamp(config.render_timestamp)
    title = record.name or record.stix_id
    lines: list[str] = [f"# Detection Strategy: {title}"]

    lines.extend(_render_section("Goal", _render_mitre_block(record.name or UNKNOWN)))
    lines.extend(_render_section("Categorization", _render_categorization(record, extraction)))
    lines.extend(_render_section("Strategy Abstract", _render_mitre_block(record.description or UNKNOWN)))
    lines.extend(_render_section(
        "Technical Context",
        _render_technical_context(record, config.profile),
    ))
    lines.extend(_render_section("Blind Spots and Assumptions", _render_mitre_block(UNKNOWN)))
    lines.extend(_render_section("False Positives", _render_mitre_block(UNKNOWN)))
    lines.extend(_render_section("Validation", _render_validation(record, config.profile)))
    lines.extend(_render_section("Priority", _render_priority(record, config.profile)))
    lines.extend(_render_section("Response", _render_mitre_block(UNKNOWN)))
    resources = _render_strategy_resources(record)
    lines.extend(_render_section("Additional Resources", resources))

    lines.append("### Provenance")
    lines.extend(_render_provenance(record, extraction, config))

    return "\n".join(lines).rstrip() + "\n"

def _render_section(title: str, content: str | Iterable[str]) -> list[str]:
    lines = [f"## {title}"]
    if isinstance(content, str):
        lines.append(content)
    else:
        content_lines = list(content)
        if not content_lines:
            lines.append(UNKNOWN)
        else:
            lines.extend(content_lines)
    return lines

def _render_categorization(
    record: DetectionStrategyRecord,
    extraction: ExtractionResult,
) -> list[str]:
    external_id = record.external_id or UNKNOWN
    platforms = _format_list(record.platforms)
    domains = _format_list(record.domains)
    rows = [
        ("Detection Strategy External ID", external_id),
        ("Detection Strategy STIX ID", record.stix_id),
        ("ATT&CK Domain", extraction.domain),
        ("Platforms", platforms),
        ("Domains", domains),
    ]
    return ["### Source: MITRE ATT&CK", *_render_kv_table(rows)]

def _render_technical_context(
    record: DetectionStrategyRecord,
    profile: ProfileOverlay | None,
) -> list[str]:
    data_sources = _format_list(record.data_sources)
    platforms = _format_list(record.platforms)
    lines = ["### Strategy Context (Source: MITRE ATT&CK)"]
    lines.extend(_render_kv_table([
        ("Platforms", platforms),
        ("Data Sources", data_sources),
    ]))
    related = _collect_related_labels_for_strategy(record)
    related_rows = []
    if related["data_sources"]:
        related_rows.append(("Related Data Sources (MITRE objects)", ", ".join(related["data_sources"])))
    if related["data_components"]:
        related_rows.append(("Related Data Components (MITRE objects)", ", ".join(related["data_components"])))
    if related["mitigations"]:
        related_rows.append(("Related Mitigations (MITRE objects)", ", ".join(related["mitigations"])))
    if related["software"]:
        related_rows.append(("Related Software/Tools (MITRE objects)", ", ".join(related["software"])))
    if related_rows:
        lines.append("")
        lines.append("### Related MITRE Objects (Source: MITRE ATT&CK)")
        lines.extend(_render_kv_table(related_rows))
    analytic_details = _render_analytic_details(record)
    if analytic_details:
        lines.append("")
        lines.append("### Analytics (Source: MITRE ATT&CK)")
        lines.extend(analytic_details)
    applicability = _resolve_overlay_value(
        profile,
        record,
        overlay_type="applicability",
    )
    if applicability:
        lines.append("")
        lines.append("### Overlay (Local Profile)")
        lines.append(f"- Overlay (profile): Applicability = {applicability}")
    return lines

def _render_strategy_resources(record: DetectionStrategyRecord) -> list[str]:
    refs = list(record.external_references)
    for source in record.data_source_objects:
        refs.extend(source.external_references)
    for component in record.data_component_objects:
        refs.extend(component.external_references)
    for mitigation in record.mitigations:
        refs.extend(mitigation.external_references)
    for software in record.software:
        refs.extend(software.external_references)
    rendered = _format_external_references(refs)
    if not rendered:
        return []
    return [
        "### Source: MITRE ATT&CK",
        *_render_single_column_table("Reference", rendered),
    ]

def _render_provenance(
    record: DetectionStrategyRecord,
    extraction: ExtractionResult,
    config: RenderConfig,
) -> list[str]:
    technique_external_ids = _extract_technique_external_ids(
        _collect_technique_refs(record),
    )
    analytic_ids = [a.stix_id for a in record.analytics]
    analytic_ids_str = ", ".join(analytic_ids) if analytic_ids else UNKNOWN
    technique_ids_str = ", ".join(technique_external_ids) if technique_external_ids else UNKNOWN
    bundle_id = extraction.meta.bundle_id or UNKNOWN
    bundle_spec = extraction.meta.spec_version or UNKNOWN
    external_id = record.external_id or UNKNOWN
    rows = [
        ("ATT&CK Domain", extraction.domain),
        ("STIX Bundle ID", bundle_id),
        ("STIX Spec Version", bundle_spec),
        ("STIX Bundle Hash (sha256)", extraction.meta.sha256),
        ("Generator Version", config.generator_version),
        ("Company Profile ID", config.company_profile_id),
        ("Company Profile Hash", config.company_profile_hash),
        ("Render Timestamp", config.render_timestamp),
        ("Detection Strategy STIX ID", record.stix_id),
        ("Detection Strategy External ID", external_id),
        ("Analytic STIX IDs", analytic_ids_str),
        ("Technique External IDs (explicit)", technique_ids_str),
    ]
    return _render_kv_table(rows)

def _format_list(values: tuple[str, ...]) -> str:
    if not values:
        return UNKNOWN
    return ", ".join(values)

def _analytic_label(analytic) -> str:
    return analytic.name or analytic.stix_id

def _collect_related_labels_for_strategy(
    record: DetectionStrategyRecord,
) -> dict[str, list[str]]:
    data_sources = _dedupe_records(record.data_source_objects)
    data_components = _dedupe_records(record.data_component_objects)
    mitigations = _dedupe_records(record.mitigations)
    software = _dedupe_records(record.software)
    return {
        "data_sources": _unique_labels(data_sources),
        "data_components": _unique_labels(data_components),
        "mitigations": _unique_labels(mitigations),
        "software": _unique_labels(software, include_type=True),
    }

def _collect_related_labels_for_analytic(analytic) -> dict[str, list[str]]:
    data_sources = _dedupe_records(analytic.data_source_objects)
    data_components = _dedupe_records(analytic.data_component_objects)
    mitigations = _dedupe_records(analytic.mitigations)
    software = _dedupe_records(analytic.software)
    return {
        "data_sources": _unique_labels(data_sources),
        "data_components": _unique_labels(data_components),
        "mitigations": _unique_labels(mitigations),
        "software": _unique_labels(software, include_type=True),
    }

def _dedupe_records(records):
    seen = set()
    deduped = []
    for record in records:
        if record.stix_id in seen:
            continue
        seen.add(record.stix_id)
        deduped.append(record)
    return deduped

def _unique_labels(records, include_type: bool = False) -> list[str]:
    labels = [_record_label(r, include_type=include_type) for r in records]
    return labels

def _record_label(record, include_type: bool = False) -> str:
    label = record.name or record.stix_id
    if include_type and hasattr(record, "software_type"):
        label = f"{label} [{record.software_type}]"
    if record.external_id:
        return f"{label} ({record.external_id})"
    return label

def _render_analytic_details(record: DetectionStrategyRecord) -> list[str]:
    analytics = _collect_analytic_details(record)
    lines: list[str] = []
    for analytic in analytics:
        name = analytic.name or analytic.stix_id
        external_ids = _extract_external_ids(analytic.external_references)
        external_ids_str = ", ".join(external_ids) if external_ids else UNKNOWN
        platforms = _format_list(analytic.platforms)
        description = analytic.description or UNKNOWN
        log_sources = _format_log_source_references(analytic.log_source_references)
        mutable_elements = _format_mutable_elements(analytic.mutable_elements)
        if lines:
            lines.append("")
        lines.extend([
            f"#### Analytic: {name}",
            f"- Analytic External IDs: {external_ids_str}",
            f"- Analytic STIX ID: {analytic.stix_id}",
            f"- Analytic Platforms: {platforms}",
            f"- Analytic Description: {description}",
            f"- Analytic Log Source References: {log_sources}",
            f"- Analytic Mutable Elements: {mutable_elements}",
        ])
        related_rows = _render_related_rows(_collect_related_labels_for_analytic(analytic))
        if related_rows:
            lines.append("")
            lines.append("##### Related MITRE Objects (Source: MITRE ATT&CK)")
            lines.extend(_render_kv_table(related_rows))
        resources = _render_analytic_resources(analytic)
        if resources:
            lines.append("")
            lines.append("##### Additional Resources (Source: MITRE ATT&CK)")
            lines.extend(_render_single_column_table("Reference", resources))
    if record.analytic_ref_unresolved:
        if lines:
            lines.append("")
        missing = ", ".join(record.analytic_ref_unresolved)
        lines.append(f"- Analytic References Unresolved (explicit): {missing}")
    return lines

def _collect_analytic_details(record: DetectionStrategyRecord):
    analytics: list = []
    seen = set()
    for analytic in record.analytics + record.analytic_ref_objects:
        if analytic.stix_id in seen:
            continue
        seen.add(analytic.stix_id)
        analytics.append(analytic)
    return analytics

def _extract_external_ids(refs: Iterable[ExternalReference]) -> list[str]:
    external_ids: list[str] = []
    seen = set()
    for ref in refs:
        if ref.external_id:
            if ref.external_id in seen:
                continue
            seen.add(ref.external_id)
            external_ids.append(ref.external_id)
    return external_ids

def _format_log_source_references(refs) -> str:
    if not refs:
        return UNKNOWN
    items = []
    for ref in refs:
        data_component = ref.data_component_ref or UNKNOWN
        name = ref.name or UNKNOWN
        channel = ref.channel or UNKNOWN
        items.append(f"{data_component} | {name} | {channel}")
    return "; ".join(items)

def _format_mutable_elements(elements) -> str:
    if not elements:
        return UNKNOWN
    items = []
    for element in elements:
        field = element.field or UNKNOWN
        description = element.description or UNKNOWN
        items.append(f"{field}: {description}")
    return "; ".join(items)

def _format_external_references(refs: Iterable[ExternalReference]) -> list[str]:
    rendered: list[str] = []
    for ref in refs:
        parts = []
        if ref.source_name:
            parts.append(ref.source_name)
        if ref.external_id:
            parts.append(f"external_id={ref.external_id}")
        if ref.url:
            parts.append(ref.url)
        if ref.description:
            parts.append(ref.description)
        if parts:
            rendered.append(" | ".join(parts))
    return rendered

def _render_related_rows(related: dict[str, list[str]]) -> list[tuple[str, str]]:
    related_rows = []
    if related["data_sources"]:
        related_rows.append(("Related Data Sources (MITRE objects)", ", ".join(related["data_sources"])))
    if related["data_components"]:
        related_rows.append(("Related Data Components (MITRE objects)", ", ".join(related["data_components"])))
    if related["mitigations"]:
        related_rows.append(("Related Mitigations (MITRE objects)", ", ".join(related["mitigations"])))
    if related["software"]:
        related_rows.append(("Related Software/Tools (MITRE objects)", ", ".join(related["software"])))
    return related_rows

def _render_analytic_resources(analytic) -> list[str]:
    refs = list(analytic.external_references)
    for source in analytic.data_source_objects:
        refs.extend(source.external_references)
    for component in analytic.data_component_objects:
        refs.extend(component.external_references)
    for mitigation in analytic.mitigations:
        refs.extend(mitigation.external_references)
    for software in analytic.software:
        refs.extend(software.external_references)
    return _format_external_references(refs)

def _extract_technique_external_ids(
    technique_groups: Iterable[TechniqueRef],
) -> list[str]:
    external_ids: list[str] = []
    seen = set()
    for ref in technique_groups:
        if ref.external_id:
            if ref.external_id in seen:
                continue
            seen.add(ref.external_id)
            external_ids.append(ref.external_id)
    return external_ids

def _collect_technique_refs(record: DetectionStrategyRecord) -> list[TechniqueRef]:
    refs = list(record.technique_refs)
    for analytic in record.analytics:
        refs.extend(analytic.technique_refs)
    return refs

def _resolve_overlay_value(
    profile: ProfileOverlay | None,
    record: DetectionStrategyRecord,
    overlay_type: str,
) -> str | None:
    if profile is None:
        return None
    if overlay_type == "priority":
        value = profile.priority_by_stix_id.get(record.stix_id)
        if value is None and record.external_id:
            value = profile.priority_by_external_id.get(record.external_id)
        if value is None:
            value = profile.priority_default
        return value
    if overlay_type == "applicability":
        value = profile.applicability_by_stix_id.get(record.stix_id)
        if value is None and record.external_id:
            value = profile.applicability_by_external_id.get(record.external_id)
        return value
    if overlay_type == "validation":
        value = profile.validation_by_stix_id.get(record.stix_id)
        if value is None and record.external_id:
            value = profile.validation_by_external_id.get(record.external_id)
        return value
    return None

def _render_priority(
    record: DetectionStrategyRecord,
    profile: ProfileOverlay | None,
) -> str | list[str]:
    overlay = _resolve_overlay_value(profile, record, overlay_type="priority")
    if overlay:
        return [
            "### Source: MITRE ATT&CK",
            UNKNOWN,
            "### Overlay (Local Profile)",
            f"- Overlay (profile): Priority = {overlay}",
        ]
    return _render_mitre_block(UNKNOWN)

def _render_validation(
    record: DetectionStrategyRecord,
    profile: ProfileOverlay | None,
) -> str | list[str]:
    overlay = _resolve_overlay_value(profile, record, overlay_type="validation")
    if overlay:
        return [
            "### Source: MITRE ATT&CK",
            UNKNOWN,
            "### Overlay (Local Profile)",
            f"- Overlay (profile): Validation Status = {overlay}",
        ]
    return _render_mitre_block(UNKNOWN)

def _validate_timestamp(timestamp: str) -> None:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    try:
        datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO-8601 timestamp: {timestamp}") from exc

def _render_mitre_block(content: str) -> list[str]:
    return ["### Source: MITRE ATT&CK", content]

def _render_kv_table(rows: Iterable[tuple[str, str]]) -> list[str]:
    lines = ["| Field | Value |", "| --- | --- |"]
    for field, value in rows:
        lines.append(
            f"| {_escape_table_cell(field)} | {_escape_table_cell(value)} |",
        )
    return lines

def _render_single_column_table(header: str, values: Iterable[str]) -> list[str]:
    lines = [f"| {_escape_table_cell(header)} |", "| --- |"]
    for value in values:
        lines.append(f"| {_escape_table_cell(value)} |")
    return lines

def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|")
