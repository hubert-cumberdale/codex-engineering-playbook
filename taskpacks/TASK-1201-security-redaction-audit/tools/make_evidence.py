from __future__ import annotations

import json
import platform
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.redaction import redact_with_evidence  # noqa: E402

ART = ROOT / "artifacts"
SRC = ROOT / "src" / "sample_input.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    raw = SRC.read_text(encoding="utf-8")
    res = redact_with_evidence(raw)

    (ART / "redacted_sample.txt").write_text(res.redacted_text, encoding="utf-8")

    evidence = {
        "taskpack_id": "TASK-1201-security-redaction-audit",
        "tool": {"name": "make_evidence.py", "python": platform.python_version()},
        "inputs": {
            "sample_input_path": str(SRC.relative_to(ROOT)),
            "input_sha256": res.input_sha256,
        },
        "outputs": {
            "redacted_sample_path": "artifacts/redacted_sample.txt",
            "output_sha256": res.output_sha256,
        },
        "redaction_counts": res.counts,
    }

    (ART / "evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("EVIDENCE_WRITTEN artifacts/evidence.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
