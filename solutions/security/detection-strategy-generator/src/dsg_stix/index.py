from __future__ import annotations

from typing import Any

from .models import Relationship, StixObject

def wrap_objects(bundle_obj: dict[str, Any]) -> list[StixObject]:
    out: list[StixObject] = []
    for o in bundle_obj.get("objects", []):
        if not isinstance(o, dict):
            continue
        oid = o.get("id")
        otype = o.get("type")
        if isinstance(oid, str) and isinstance(otype, str):
            out.append(StixObject(type=otype, id=oid, raw=dict(o)))
    # deterministic order
    out.sort(key=lambda x: (x.type, x.id))
    return out

def extract_relationships(objects: list[StixObject]) -> list[Relationship]:
    rels: list[Relationship] = []
    for o in objects:
        if o.type != "relationship":
            continue
        raw = o.raw
        rid = raw.get("id")
        rtype = raw.get("relationship_type")
        src = raw.get("source_ref")
        tgt = raw.get("target_ref")
        if all(isinstance(x, str) for x in (rid, rtype, src, tgt)):
            rels.append(Relationship(
                id=rid,
                relationship_type=rtype,
                source_ref=src,
                target_ref=tgt,
                raw=dict(raw),
            ))
    rels.sort(key=lambda r: (r.relationship_type, r.source_ref, r.target_ref, r.id))
    return rels

def index_by_id(objects: list[StixObject]) -> dict[str, StixObject]:
    # deterministic: last write wins, but stable order means stable outcome
    out: dict[str, StixObject] = {}
    for o in objects:
        out[o.id] = o
    return out
