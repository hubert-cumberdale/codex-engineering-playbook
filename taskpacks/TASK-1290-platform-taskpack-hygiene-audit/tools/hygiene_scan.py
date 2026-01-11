from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "taskpacks" / "TASK-1290-platform-taskpack-hygiene-audit" / "artifacts"

TEST_DISCOVER_RE = re.compile(r"unittest.*discover")
TIMESTAMP_KEYS = ("timestamp", "generated_at", "created_at")

def scan_taskpacks():
    findings = []
    tp_root = ROOT / "taskpacks"

    for tp in tp_root.iterdir():
        if not tp.is_dir():
            continue
        if not (tp / "task.yml").exists():
            continue  # ignore non-taskpack dirs

        # Required files
        for req in ("spec.md", "acceptance.yml", "risk.md", "runbook.md"):
            if not (tp / req).exists():
                findings.append({
                    "taskpack": tp.name,
                    "type": "missing_file",
                    "detail": req,
                })

        # Acceptance hygiene
        acc = tp / "acceptance.yml"
        if acc.exists():
            text = acc.read_text(encoding="utf-8")
            if "unittest" in text and not TEST_DISCOVER_RE.search(text):
                findings.append({
                    "taskpack": tp.name,
                    "type": "acceptance_pattern",
                    "detail": "unittest without explicit discover",
                })

        # Import footgun heuristic
        for tool in (tp / "tools").glob("*.py"):
            t = tool.read_text(encoding="utf-8")
            if "from src." in t and "sys.path.insert" not in t:
                findings.append({
                    "taskpack": tp.name,
                    "type": "import_path",
                    "detail": f"{tool.name} imports src without sys.path bootstrap",
                })

    return findings


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    findings = scan_taskpacks()

    report = {
        "taskpack_id": "TASK-1290-platform-taskpack-hygiene-audit",
        "finding_count": len(findings),
        "findings": findings,
        "status": "ok",
    }

    (ART / "hygiene_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md = ["# Platform Hygiene Report", ""]
    md.append(f"- Findings: {len(findings)}")
    md.append("")
    for f in findings:
        md.append(f"- **{f['taskpack']}** — {f['type']}: {f['detail']}")
    md.append("")

    (ART / "hygiene_report.md").write_text("\n".join(md), encoding="utf-8")

    print("HYGIENE_SCAN_COMPLETE artifacts/hygiene_report.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
