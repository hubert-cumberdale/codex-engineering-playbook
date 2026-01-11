from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import read_csv, render_markdown, summarize  # noqa: E402

ART = ROOT / "artifacts"
CSV_PATH = ROOT / "data" / "sample_coverage.csv"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    rows, csv_sha = read_csv(str(CSV_PATH))
    summ = summarize(rows)
    md = render_markdown(rows, summ)

    report_json = {
        "taskpack_id": "TASK-1204-security-csv-report-validate",
        "source_csv": {
            "path": "data/sample_coverage.csv",
            "sha256": csv_sha,
        },
        "summary": summ,
        "detail_rows": [
            {
                "technique_id": r.technique_id,
                "control_id": r.control_id,
                "status": r.status,
                "owner": r.owner,
            }
            for r in sorted(rows, key=lambda x: (x.technique_id, x.control_id))
        ],
    }

    (ART / "report.json").write_text(
        json.dumps(report_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (ART / "report.md").write_text(md, encoding="utf-8")

    print("REPORT_WRITTEN artifacts/report.json artifacts/report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
