from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from ..models import ExtractionResult
from ..records.models import DetectionStrategyRecord, ExternalReference, TechniqueRef
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

def render_detection_strategy(
    record: DetectionStrategyRecord,
    extraction: ExtractionResult,
    config: RenderConfig,
) -> str:
    _validate_timestamp(config.render_timestamp)
    title = record.name or record.stix_id
    lines: list[str] = [f"# Detection Strategy: {title}"]

    lines.extend(_render_section("Goal", record.name or UNKNOWN))
    lines.extend(_render_section("Categorization", _render_categorization(record, extraction)))
    lines.extend(_render_section("Strategy Abstract", record.description or UNKNOWN))
    lines.extend(_render_section("Technical Context", _render_technical_context(record)))
    lines.extend(_render_section("Blind Spots and Assumptions", UNKNOWN))
    lines.extend(_render_section("False Positives", UNKNOWN))
    lines.extend(_render_section("Validation", UNKNOWN))
    lines.extend(_render_section("Priority", UNKNOWN))
    lines.extend(_render_section("Response", UNKNOWN))
    lines.extend(_render_section("Additional Resources", _render_resources(record)))

    lines.append("## Provenance")
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
    return [
        f"- Detection Strategy External ID: {external_id}",
        f"- Detection Strategy STIX ID: {record.stix_id}",
        f"- ATT&CK Domain: {extraction.domain}",
        f"- Platforms: {platforms}",
        f"- Domains: {domains}",
        f"- Analytics Included: {len(record.analytics)}",
    ]

def _render_technical_context(record: DetectionStrategyRecord) -> list[str]:
    analytics = _format_list(tuple(_analytic_label(a) for a in record.analytics))
    data_sources = _format_list(record.data_sources)
    platforms = _format_list(record.platforms)
    return [
        f"- Platforms: {platforms}",
        f"- Data Sources: {data_sources}",
        f"- Analytics: {analytics}",
    ]

def _render_resources(record: DetectionStrategyRecord) -> list[str]:
    refs = list(record.external_references)
    for analytic in record.analytics:
        refs.extend(analytic.external_references)
    rendered = [f"- {item}" for item in _format_external_references(refs)]
    return rendered or [UNKNOWN]

def _render_provenance(
    record: DetectionStrategyRecord,
    extraction: ExtractionResult,
    config: RenderConfig,
) -> list[str]:
    technique_external_ids = _extract_technique_external_ids(
        _collect_technique_refs(record),
    )
    analytic_ids = [a.stix_id for a in record.analytics]
    analytic_ids_str = ", ".join(sorted(analytic_ids)) if analytic_ids else UNKNOWN
    technique_ids_str = ", ".join(technique_external_ids) if technique_external_ids else UNKNOWN
    bundle_id = extraction.meta.bundle_id or UNKNOWN
    bundle_spec = extraction.meta.spec_version or UNKNOWN
    external_id = record.external_id or UNKNOWN
    return [
        f"- ATT&CK Domain: {extraction.domain}",
        f"- STIX Bundle ID: {bundle_id}",
        f"- STIX Spec Version: {bundle_spec}",
        f"- STIX Bundle Hash (sha256): {extraction.meta.sha256}",
        f"- Generator Version: {config.generator_version}",
        f"- Company Profile ID: {config.company_profile_id}",
        f"- Company Profile Hash: {config.company_profile_hash}",
        f"- Render Timestamp: {config.render_timestamp}",
        f"- Detection Strategy STIX ID: {record.stix_id}",
        f"- Detection Strategy External ID: {external_id}",
        f"- Analytic STIX IDs: {analytic_ids_str}",
        f"- Technique External IDs (explicit): {technique_ids_str}",
    ]

def _format_list(values: tuple[str, ...]) -> str:
    if not values:
        return UNKNOWN
    return ", ".join(values)

def _analytic_label(analytic) -> str:
    return analytic.name or analytic.stix_id

def _format_external_references(refs: Iterable[ExternalReference]) -> list[str]:
    rendered: list[str] = []
    for ref in sorted(refs, key=lambda r: (
        r.source_name or "",
        r.url or "",
        r.external_id or "",
        r.description or "",
    )):
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

def _extract_technique_external_ids(
    technique_groups: Iterable[TechniqueRef],
) -> list[str]:
    external_ids: set[str] = set()
    for ref in technique_groups:
        if ref.external_id:
            external_ids.add(ref.external_id)
    return sorted(external_ids)

def _collect_technique_refs(record: DetectionStrategyRecord) -> list[TechniqueRef]:
    refs = list(record.technique_refs)
    for analytic in record.analytics:
        refs.extend(analytic.technique_refs)
    return refs

def _validate_timestamp(timestamp: str) -> None:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    try:
        datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO-8601 timestamp: {timestamp}") from exc
