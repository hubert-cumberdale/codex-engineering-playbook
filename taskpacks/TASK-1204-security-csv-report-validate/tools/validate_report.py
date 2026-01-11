from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ART = ROOT / "artifacts"
REPORT = ART / "report.json"


def err(path: str, msg: str) -> Dict[str, str]:
    return {"path": path, "error": msg}


def require(d: Dict[str, Any], key: str, path: str) -> Tuple[bool, Any, Dict[str, str] | None]:
    if key not in d:
        return False, None, err(path, f"missing key '{key}'")
    return True, d[key], None


def main() -> int:
    errors: List[Dict[str, str]] = []

    if not REPORT.exists():
        errors.append(err("artifacts/report.json", "report.json does not exist"))
        status = "failed"
    else:
        data = json.loads(REPORT.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            errors.append(err("$", "report must be an object"))
        else:
            ok, v, e = require(data, "taskpack_id", "$")
            if not ok:
                errors.append(e)  # type: ignore[arg-type]
            elif v != "TASK-1204-security-csv-report-validate":
                errors.append(err("$.taskpack_id", "unexpected taskpack_id"))

            ok, source, e = require(data, "source_csv", "$")
            if not ok:
                errors.append(e)  # type: ignore[arg-type]
            elif not isinstance(source, dict):
                errors.append(err("$.source_csv", "must be an object"))
            else:
                if source.get("path") != "data/sample_coverage.csv":
                    errors.append(err("$.source_csv.path", "unexpected path"))
                sha = source.get("sha256")
                if not isinstance(sha, str) or len(sha) != 64:
                    errors.append(err("$.source_csv.sha256", "must be 64-char hex string"))

            ok, summ, e = require(data, "summary", "$")
            if not ok:
                errors.append(e)  # type: ignore[arg-type]
            elif not isinstance(summ, dict):
                errors.append(err("$.summary", "must be an object"))
            else:
                tr = summ.get("total_rows")
                if not isinstance(tr, int) or tr < 1:
                    errors.append(err("$.summary.total_rows", "must be a positive integer"))

                bs = summ.get("by_status")
                if not isinstance(bs, dict):
                    errors.append(err("$.summary.by_status", "must be an object"))
                else:
                    for k in ("covered", "partial", "missing"):
                        if k not in bs:
                            errors.append(err("$.summary.by_status", f"missing key '{k}'"))
                        elif not isinstance(bs[k], int) or bs[k] < 0:
                            errors.append(err(f"$.summary.by_status.{k}", "must be a non-negative integer"))

            detail = data.get("detail_rows")
            if not isinstance(detail, list) or not detail:
                errors.append(err("$.detail_rows", "must be a non-empty list"))

        status = "ok" if not errors else "failed"

    evidence = {
        "taskpack_id": "TASK-1204-security-csv-report-validate",
        "validated_path": "artifacts/report.json",
        "status": status,
        "errors": errors,
    }

    ART.mkdir(parents=True, exist_ok=True)
    (ART / "schema_validation.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if errors:
        print("SCHEMA_VALIDATION_FAILED artifacts/schema_validation.json")
        for e in errors:
            print(f"- {e['path']}: {e['error']}")
        return 1

    print("SCHEMA_VALIDATION_OK artifacts/schema_validation.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
