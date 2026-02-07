from __future__ import annotations

from typing import Any

from .index import extract_relationships, wrap_objects
from .models import ExtractionResult

DEFAULT_DETECTION_STRATEGY_TYPES = ("x-mitre-detection-strategy",)
DEFAULT_ANALYTIC_TYPES = ("x-mitre-analytic",)
DEFAULT_DATA_SOURCE_TYPES = ("x-mitre-data-source",)
DEFAULT_DATA_COMPONENT_TYPES = ("x-mitre-data-component",)
DEFAULT_MITIGATION_TYPES = ("course-of-action",)
DEFAULT_SOFTWARE_TYPES = ("tool", "malware")

TECHNIQUE_TYPES = ("attack-pattern",)  # standard ATT&CK technique SDO type

def extract_stage1(
    bundle_obj: dict[str, Any],
    meta,
    domain: str,
    detection_strategy_types=DEFAULT_DETECTION_STRATEGY_TYPES,
    analytic_types=DEFAULT_ANALYTIC_TYPES,
    data_source_types=DEFAULT_DATA_SOURCE_TYPES,
    data_component_types=DEFAULT_DATA_COMPONENT_TYPES,
    mitigation_types=DEFAULT_MITIGATION_TYPES,
    software_types=DEFAULT_SOFTWARE_TYPES,
) -> ExtractionResult:
    objects = wrap_objects(bundle_obj)
    rels = extract_relationships(objects)

    ds = tuple(o for o in objects if o.type in detection_strategy_types)
    an = tuple(o for o in objects if o.type in analytic_types)
    techniques = tuple(o for o in objects if o.type in TECHNIQUE_TYPES)
    data_sources = tuple(o for o in objects if o.type in data_source_types)
    data_components = tuple(o for o in objects if o.type in data_component_types)
    mitigations = tuple(o for o in objects if o.type in mitigation_types)
    software = tuple(o for o in objects if o.type in software_types)

    # Explicit technique external ids: only from technique objects present in the bundle.
    # We DO NOT infer from names, descriptions, or external refs on other objects.
    technique_external_ids: set[str] = set()
    for o in objects:
        if o.type in TECHNIQUE_TYPES:
            for ref in o.raw.get("external_references", []) or []:
                if isinstance(ref, dict):
                    eid = ref.get("external_id")
                    if isinstance(eid, str):
                        technique_external_ids.add(eid)

    return ExtractionResult(
        meta=meta,
        domain=domain,
        detection_strategies=tuple(sorted(ds, key=lambda x: x.id)),
        analytics=tuple(sorted(an, key=lambda x: x.id)),
        relationships=tuple(rels),
        techniques=tuple(sorted(techniques, key=lambda x: x.id)),
        data_sources=tuple(sorted(data_sources, key=lambda x: x.id)),
        data_components=tuple(sorted(data_components, key=lambda x: x.id)),
        mitigations=tuple(sorted(mitigations, key=lambda x: x.id)),
        software=tuple(sorted(software, key=lambda x: x.id)),
        explicit_technique_external_ids=tuple(sorted(technique_external_ids)),
    )
