from pathlib import Path
import json

from dsg_stix.io import load_bundle_bytes, bundle_meta
from dsg_stix.extract import extract_stage1

def test_deterministic_output_bytes_identical():
    p = Path(__file__).parent / "fixtures" / "minimal_bundle.json"
    b1, obj1 = load_bundle_bytes(p)
    meta1 = bundle_meta(b1, obj1)
    r1 = extract_stage1(obj1, meta1, domain="enterprise")

    b2, obj2 = load_bundle_bytes(p)
    meta2 = bundle_meta(b2, obj2)
    r2 = extract_stage1(obj2, meta2, domain="enterprise")

    payload1 = {
        "meta": {"sha256": r1.meta.sha256, "object_count": r1.meta.object_count},
        "ds": [o.id for o in r1.detection_strategies],
        "an": [o.id for o in r1.analytics],
        "rels": [rel.id for rel in r1.relationships],
    }
    payload2 = {
        "meta": {"sha256": r2.meta.sha256, "object_count": r2.meta.object_count},
        "ds": [o.id for o in r2.detection_strategies],
        "an": [o.id for o in r2.analytics],
        "rels": [rel.id for rel in r2.relationships],
    }

    assert json.dumps(payload1, sort_keys=True) == json.dumps(payload2, sort_keys=True)
