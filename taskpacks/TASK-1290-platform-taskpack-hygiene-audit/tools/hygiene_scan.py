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
            continue

        name = tp.name

        # --- Required files ---
        for req in ("spec.md", "acceptance.yml", "risk.md", "runbook.md"):
            if not (tp / req).exists():
                findings.append({
                    "taskpack": name,
                    "type": "missing_file",
                    "detail": req,
                })

        # --- Acceptance hygiene ---
        acc = tp / "acceptance.yml"
        acc_text = acc.read_text(encoding="utf-8") if acc.exists() else ""
        if "compileall" not in acc_text:
            findings.append({
                "taskpack": name,
                "type": "acceptance_pattern",
                "detail": "compileall missing from acceptance",
            })
        if "lint_check.py" not in acc_text:
            findings.append({
                "taskpack": name,
                "type": "acceptance_pattern",
                "detail": "lint_check missing from acceptance",
            })
        if "unittest" in acc_text and not TEST_DISCOVER_RE.search(acc_text):
            findings.append({
                "taskpack": name,
                "type": "acceptance_pattern",
                "detail": "unittest without explicit discover",
            })

        # --- Import path footgun ---
        for tool in (tp / "tools").glob("*.py"):
            t = tool.read_text(encoding="utf-8")
            if "from src." in t and "sys.path.insert" not in t:
                findings.append({
                    "taskpack": name,
                    "type": "import_path",
                    "detail": f"{tool.name} imports src without sys.path bootstrap",
                })

            # Artifact path hygiene
            if ".write_text(" in t and "artifacts" not in t:
                findings.append({
                    "taskpack": name,
                    "type": "artifact_path",
                    "detail": f"{tool.name} may write files outside artifacts/",
                })

        # --- Manifest recommendation ---
        art = tp / "artifacts"
        if art.exists():
            files = [p for p in art.iterdir() if p.is_file() and p.name != "README.md"]
            if len(files) > 1 and not (art / "manifest.json").exists():
                findings.append({
                    "taskpack": name,
                    "type": "manifest",
                    "detail": "multiple artifacts without artifacts/manifest.json",
                })

        # --- Deploy / network language ---
        for doc in ("spec.md", "runbook.md", "risk.md"):
            p = tp / doc
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8").lower()
            for word in ("deploy", "deployment", "publish", "hosting", "release", "cloud"):
                if word in text:
                    findings.append({
                        "taskpack": name,
                        "type": "language",
                        "detail": f"{doc} contains '{word}'",
                    })

        # --- Timestamp smell in JSON artifacts ---
        for jf in art.glob("*.json") if art.exists() else []:
            text = jf.read_text(encoding="utf-8").lower()
            for k in TIMESTAMP_KEYS:
                if f'"{k}"' in text:
                    findings.append({
                        "taskpack": name,
                        "type": "determinism",
                        "detail": f"{jf.name} contains timestamp-like key '{k}'",
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
