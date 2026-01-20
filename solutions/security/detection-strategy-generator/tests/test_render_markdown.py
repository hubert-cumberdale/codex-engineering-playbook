from pathlib import Path
import re

from dsg_stix.extract import extract_stage1
from dsg_stix.io import bundle_meta, load_bundle_bytes
from dsg_stix.records import build_records
from dsg_stix.render import RenderConfig, render_detection_strategy
from dsg_stix.render.markdown import SECTION_HEADERS

FIXTURE_TIMESTAMP = "2024-01-01T00:00:00Z"

def _load_minimal_record():
    fixture = Path(__file__).parent / "fixtures" / "minimal_bundle.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    assert len(records) == 1
    return extraction, records[0]

def _load_enterprise_records():
    fixture = Path(__file__).parent / "fixtures" / "enterprise-attack.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    return extraction, records

def test_render_minimal_matches_fixture():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    expected_path = Path(__file__).parent / "fixtures" / "expected_minimal_ads.md"
    expected = expected_path.read_text(encoding="utf-8")
    assert rendered == expected

def test_render_sections_present_and_ordered():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    headers = re.findall(r"^## (.+)$", rendered, flags=re.MULTILINE)
    assert headers[:len(SECTION_HEADERS)] == list(SECTION_HEADERS)

def test_provenance_block_present_and_correct():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert "## Provenance" in rendered
    assert "- STIX Bundle Hash (sha256):" in rendered
    assert f"- Render Timestamp: {FIXTURE_TIMESTAMP}" in rendered

def test_provenance_includes_technique_ids_when_relationships_exist():
    extraction, records = _load_enterprise_records()
    record = next(
        (r for r in records if any(ref.external_id for ref in r.technique_refs)),
        None,
    )
    if record is None:
        record = next(
            (
                r for r in records
                if any(
                    ref.external_id
                    for analytic in r.analytics
                    for ref in analytic.technique_refs
                )
            ),
            None,
        )
    assert record is not None, "Fixture lacks explicit technique relationships with external IDs."

    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)
    assert "- Technique External IDs (explicit): Not provided by source" not in rendered
