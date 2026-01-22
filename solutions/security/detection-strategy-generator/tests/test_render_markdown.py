from pathlib import Path
import json
import re

from dsg_stix.extract import extract_stage1
from dsg_stix.io import bundle_meta, load_bundle_bytes
from dsg_stix.profile import load_profile
from dsg_stix.records import build_records
from dsg_stix.render.constants import UNKNOWN
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
    fixture = Path(__file__).parent / "fixtures" / "minimal_bundle.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    return extraction, records

def _load_records_with_technique_refs():
    fixture = Path(__file__).parent / "fixtures" / "bundle_with_technique.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    return extraction, records

def _load_related_record():
    fixture = Path(__file__).parent / "fixtures" / "bundle_with_related_objects.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    assert len(records) == 1
    return extraction, records[0]

def _load_analytic_refs_record():
    fixture = Path(__file__).parent / "fixtures" / "bundle_with_analytic_refs_full.json"
    bundle_bytes, bundle_obj = load_bundle_bytes(fixture)
    meta = bundle_meta(bundle_bytes, bundle_obj)
    extraction = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain="enterprise")
    records = build_records(extraction)
    assert len(records) == 1
    return extraction, records[0]

def test_render_minimal_matches_fixture():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert rendered.startswith("# Detection Strategy: Example Detection Strategy\n")
    assert "## Goal" in rendered
    assert "### Source: MITRE ATT&CK" in rendered
    assert "## Response" in rendered
    assert "### Provenance" in rendered

def test_render_sections_present_and_ordered():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    headers = re.findall(r"^## (.+)$", rendered, flags=re.MULTILINE)
    assert "Provenance" not in headers
    expected = list(SECTION_HEADERS)
    assert len(headers) == len(expected)
    assert headers == expected

def test_provenance_block_present_and_correct():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert not re.search(r"^## Provenance$", rendered, flags=re.MULTILINE)
    assert "### Provenance" in rendered
    assert "| STIX Bundle Hash (sha256) |" in rendered
    assert f"| Render Timestamp | {FIXTURE_TIMESTAMP} |" in rendered
    assert rendered.index("### Provenance") > rendered.index("## Response")

def test_provenance_includes_technique_ids_when_relationships_exist():
    extraction, records = _load_records_with_technique_refs()
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
    assert "Technique External IDs (explicit) | Not provided by source" not in rendered

def test_render_includes_related_objects_and_analytic_metadata():
    extraction, record = _load_related_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    strategy_start = rendered.index("### Related MITRE Objects (Source: MITRE ATT&CK)")
    analytic_start = rendered.index("#### Analytic: Analytic Alpha")
    strategy_block = rendered[strategy_start:analytic_start]
    assert "Related Data Sources (MITRE objects)" not in strategy_block
    assert "Related Data Components (MITRE objects)" not in strategy_block
    assert "| Related Mitigations (MITRE objects) | Mitigation Example (M0001) |" in strategy_block
    assert "| Related Software/Tools (MITRE objects) | Tool Example [tool] (S0001), Malware Example [malware] (S0002) |" in strategy_block
    assert "#### Analytic: Analytic Alpha" in rendered
    assert "- Analytic External IDs: AN0001" in rendered
    assert "- Analytic STIX ID: x-mitre-analytic--bbbbbbbb-bbbb-4000-8000-bbbbbbbbbbbb" in rendered
    assert "- Analytic Platforms: Windows" in rendered
    assert "- Analytic Description: Explicit analytic description" in rendered
    assert "- Analytic Log Source References: Not provided by source" in rendered
    assert "- Analytic Mutable Elements: Not provided by source" in rendered
    assert "- Analytic References Unresolved (explicit): x-mitre-analytic--99999999-9999-4000-8000-999999999999" in rendered
    analytic_block = rendered[analytic_start:]
    assert "##### Related MITRE Objects (Source: MITRE ATT&CK)" in analytic_block
    assert "| Related Data Sources (MITRE objects) | Process (DS0001) |" in analytic_block
    assert "| Related Data Components (MITRE objects) | Process Creation (DC0001) |" in analytic_block
    assert "##### Additional Resources (Source: MITRE ATT&CK)" in analytic_block
    assert "mitre-attack \\| external_id=AN0001 \\| https://example.com/analytics/AN0001" in analytic_block
    assert "Ignored Source (DS9999)" not in rendered
    assert "## Additional Resources" in rendered
    assert "mitre-attack \\| external_id=M0001 \\| https://example.com/mitigations/M0001" in rendered
    assert "mitre-attack \\| external_id=S0001 \\| https://example.com/software/S0001" in rendered
    assert "mitre-attack \\| external_id=S0002 \\| https://example.com/software/S0002" in rendered

def test_profile_overlay_renders_priority_applicability_validation(tmp_path: Path):
    extraction, record = _load_minimal_record()
    profile_payload = {
        "profile_id": "acme-profile",
        "priority": {"default": "High"},
        "applicability": {"by_stix_id": {record.stix_id: "In Scope"}},
        "validation_status": {"by_stix_id": {record.stix_id: "Planned"}},
    }
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile_payload), encoding="utf-8")
    profile = load_profile(profile_path)

    config = RenderConfig(
        render_timestamp=FIXTURE_TIMESTAMP,
        company_profile_id=profile.profile_id,
        company_profile_hash=profile.profile_hash,
        profile=profile,
    )
    rendered = render_detection_strategy(record, extraction, config)

    assert "- Overlay (profile): Priority = High" in rendered
    assert "- Overlay (profile): Applicability = In Scope" in rendered
    assert "- Overlay (profile): Validation Status = Planned" in rendered
    assert f"| Company Profile ID | {profile.profile_id} |" in rendered
    assert f"| Company Profile Hash | {profile.profile_hash} |" in rendered
    assert "### Overlay (Local Profile)" in rendered

def test_analytic_refs_render_full_fields():
    extraction, record = _load_analytic_refs_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert "#### Analytic: Analytic With Log Sources" in rendered
    assert "- Analytic External IDs: AN0002" in rendered
    assert "- Analytic STIX ID: x-mitre-analytic--cdcdcdcd-cdcd-4000-8000-cdcdcdcdcdcd" in rendered
    assert "- Analytic Platforms: Linux, Windows" in rendered
    assert "- Analytic Description: Analytic description body" in rendered
    assert "- Analytic Log Source References: x-mitre-data-component--abababab-efef-4000-8000-efefefefefee | linux:syslog | Query to suspicious domain; x-mitre-data-component--efefefef-efef-4000-8000-efefefefefef | auditd:SYSCALL | socket/connect" in rendered
    assert "- Analytic Mutable Elements: DomainReputationFeed: Whitelist tuned via intel; ProcessWhitelist: Known safe daemons" in rendered

def test_overlay_sections_absent_when_profile_missing():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert "### Overlay (Local Profile)" not in rendered

def test_additional_resources_render_when_empty():
    extraction, record = _load_minimal_record()
    config = RenderConfig(render_timestamp=FIXTURE_TIMESTAMP)
    rendered = render_detection_strategy(record, extraction, config)

    assert "## Additional Resources" in rendered
    assert f"## Additional Resources\n{UNKNOWN}\n" in rendered
