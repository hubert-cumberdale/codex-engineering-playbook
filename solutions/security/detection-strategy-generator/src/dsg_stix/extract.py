from __future__ import annotations

from dataclasses import replace
from typing import Any

from .index import extract_relationships, index_by_id, wrap_objects
from .models import ExtractionResult, Relationship, StixObject

DEFAULT_DETECTION_STRATEGY_TYPES = ("x-mitre-detection-strategy",)
DEFAULT_ANALYTIC_TYPES = ("x-mitre-analytic",)

TECHNIQUE_TYPES = ("attack-pattern",)  # standard ATT&CK technique SDO type

def extract_stage1(
    bundle_obj: dict[str, Any],
    meta,
    domain: str,
    detection_strategy_types=DEFAULT_DETECTION_STRATEGY_TYPES,
    analytic_types=DEFAULT_ANALYTIC_TYPES,
) -> ExtractionResult:
    objects = wrap_objects(bundle_obj)
    rels = extract_relationships(objects)
    by_id = index_by_id(objects)

    ds = tuple(o for o in objects if o.type in detection_strategy_types)
    an = tuple(o for o in objects if o.type in analytic_types)

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
        explicit_technique_external_ids=tuple(sorted(technique_external_ids)),
    )
