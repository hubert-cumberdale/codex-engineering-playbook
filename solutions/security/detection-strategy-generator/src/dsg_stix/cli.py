from __future__ import annotations

import argparse
import json
from pathlib import Path
from dataclasses import asdict

from .io import load_bundle_bytes, bundle_meta
from .extract import extract_stage1

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dsg-stix")
    sub = p.add_subparsers(dest="cmd", required=True)

    ins = sub.add_parser("inspect", help="Load a STIX bundle and emit extraction JSON.")
    ins.add_argument("--domain", required=True, choices=["enterprise", "mobile", "ics"])
    ins.add_argument("--bundle", required=True, type=Path)
    ins.add_argument("--pretty", action="store_true")

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
            "relationships": [r.raw for r in result.relationships],
            "explicit_technique_external_ids": list(result.explicit_technique_external_ids),
        }
        if args.pretty:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(json.dumps(payload, sort_keys=True))
        return 0

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
