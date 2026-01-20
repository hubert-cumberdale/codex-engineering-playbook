from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from dataclasses import asdict

from .io import load_bundle_bytes, bundle_meta
from .extract import extract_stage1
from .profile import load_profile
from .records import build_records
from .render import RenderConfig, render_detection_strategy, UNKNOWN

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dsg-stix")
    sub = p.add_subparsers(dest="cmd", required=True)

    ins = sub.add_parser("inspect", help="Load a STIX bundle and emit extraction JSON.")
    ins.add_argument("--domain", required=True, choices=["enterprise", "mobile", "ics"])
    ins.add_argument("--bundle", required=True, type=Path)
    ins.add_argument("--pretty", action="store_true")

    rnd = sub.add_parser("render", help="Render ADS-style Markdown docs from a STIX bundle.")
    rnd.add_argument("--domain", required=True, choices=["enterprise", "mobile", "ics"])
    rnd.add_argument("--bundle", required=True, type=Path)
    rnd.add_argument("--output-dir", required=True, type=Path)
    rnd.add_argument("--timestamp", required=True, help="ISO-8601 timestamp for determinism.")
    rnd.add_argument("--profile", type=Path, help="Optional JSON profile overlay.")
    rnd.add_argument("--company-profile-id", default=UNKNOWN)
    rnd.add_argument("--company-profile-hash", default=UNKNOWN)

    args = p.parse_args(argv)

    if args.cmd == "inspect":
        bundle_bytes, bundle_obj = load_bundle_bytes(args.bundle)
        meta = bundle_meta(bundle_bytes, bundle_obj)
        result = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain=args.domain)

        payload = {
            "meta": asdict(result.meta),
            "domain": result.domain,
            "detection_strategies": [o.raw for o in result.detection_strategies],
            "analytics": [o.raw for o in result.analytics],
            "data_sources": [o.raw for o in result.data_sources],
            "data_components": [o.raw for o in result.data_components],
            "mitigations": [o.raw for o in result.mitigations],
            "software": [o.raw for o in result.software],
            "relationships": [r.raw for r in result.relationships],
            "explicit_technique_external_ids": list(result.explicit_technique_external_ids),
        }
        if args.pretty:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(json.dumps(payload, sort_keys=True))
        return 0

    if args.cmd == "render":
        bundle_bytes, bundle_obj = load_bundle_bytes(args.bundle)
        meta = bundle_meta(bundle_bytes, bundle_obj)
        result = extract_stage1(bundle_obj=bundle_obj, meta=meta, domain=args.domain)
        records = build_records(result)
        profile = load_profile(args.profile) if args.profile else None
        profile_id = profile.profile_id if profile else args.company_profile_id
        profile_hash = profile.profile_hash if profile else args.company_profile_hash
        config = RenderConfig(
            render_timestamp=args.timestamp,
            company_profile_id=profile_id,
            company_profile_hash=profile_hash,
            profile=profile,
        )

        output_root = Path(args.output_dir) / args.domain
        output_root.mkdir(parents=True, exist_ok=True)

        for record in records:
            filename = _render_filename(record)
            path = output_root / filename
            content = render_detection_strategy(record, result, config)
            path.write_text(content, encoding="utf-8")
        return 0

    return 2

def _render_filename(record) -> str:
    slug = _slugify(record.name or "detection-strategy")
    external_id = record.external_id
    if external_id:
        safe_id = re.sub(r"[^A-Za-z0-9]", "", external_id)
        if safe_id:
            return f"{safe_id}_{slug}.md"
    short_id = _short_stix_id(record.stix_id)
    return f"ds_{short_id}_{slug}.md"

def _short_stix_id(stix_id: str) -> str:
    if "--" in stix_id:
        stix_id = stix_id.split("--", 1)[1]
    stix_id = re.sub(r"[^A-Za-z0-9]", "", stix_id)
    return stix_id[:8] if stix_id else "unknown"

def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "detection-strategy"

if __name__ == "__main__":
    raise SystemExit(main())
