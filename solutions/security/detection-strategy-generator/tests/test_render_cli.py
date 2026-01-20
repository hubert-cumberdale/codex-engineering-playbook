from pathlib import Path

from dsg_stix import cli

FIXTURE_TIMESTAMP = "2024-01-01T00:00:00Z"

def test_cli_renders_bundle(tmp_path: Path):
    fixture = Path(__file__).parent / "fixtures" / "minimal_bundle.json"
    output_dir = tmp_path / "docs"
    args = [
        "render",
        "--domain", "enterprise",
        "--bundle", str(fixture),
        "--output-dir", str(output_dir),
        "--timestamp", FIXTURE_TIMESTAMP,
    ]
    rc = cli.main(args)
    assert rc == 0

    expected_path = output_dir / "enterprise" / "ds_11111111_example-detection-strategy.md"
    assert expected_path.exists()
    content = expected_path.read_text(encoding="utf-8")
    assert f"- Render Timestamp: {FIXTURE_TIMESTAMP}" in content
