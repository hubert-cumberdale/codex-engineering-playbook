from pathlib import Path

from dsg_stix.io import load_bundle_bytes, bundle_meta
from dsg_stix.extract import extract_stage1

def test_extract_minimal_fixture():
    p = Path(__file__).parent / "fixtures" / "minimal_bundle.json"
    b, obj = load_bundle_bytes(p)
    meta = bundle_meta(b, obj)

    r = extract_stage1(bundle_obj=obj, meta=meta, domain="enterprise")

    assert r.meta.object_count == 3
    assert len(r.detection_strategies) == 1
    assert len(r.analytics) == 1
    assert len(r.relationships) == 1
    assert r.relationships[0].relationship_type == "includes"
