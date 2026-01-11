from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class CoverageRow:
    technique_id: str
    control_id: str
    status: str
    owner: str
    notes: str


ALLOWED_STATUS = {"covered", "partial", "missing"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: str) -> Tuple[List[CoverageRow], str]:
    with open(path, "rb") as bf:
        raw = bf.read()
    digest = sha256_bytes(raw)


    rows: List[CoverageRow] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"technique_id", "control_id", "status", "owner", "notes"}
        if set(reader.fieldnames or []) != required:
            # Exact match keeps the example deterministic and strict.
            raise ValueError(f"CSV header mismatch: got {reader.fieldnames}, expected {sorted(required)}")

        for r in reader:
            technique_id = (r["technique_id"] or "").strip()
            control_id = (r["control_id"] or "").strip()
            status = (r["status"] or "").strip().lower()
            owner = (r["owner"] or "").strip()
            notes = (r["notes"] or "").strip()

            if not technique_id or not control_id:
                raise ValueError("technique_id and control_id must be non-empty")
            if status not in ALLOWED_STATUS:
                raise ValueError(f"invalid status: {status}")

            rows.append(
                CoverageRow(
                    technique_id=technique_id,
                    control_id=control_id,
                    status=status,
                    owner=owner,
                    notes=notes,
                )
            )

    return rows, digest


def summarize(rows: Iterable[CoverageRow]) -> Dict[str, object]:
    rows_list = list(rows)
    by_status: Dict[str, int] = {k: 0 for k in sorted(ALLOWED_STATUS)}
    by_technique: Dict[str, Dict[str, int]] = {}

    for r in rows_list:
        by_status[r.status] += 1
        if r.technique_id not in by_technique:
            by_technique[r.technique_id] = {k: 0 for k in sorted(ALLOWED_STATUS)}
        by_technique[r.technique_id][r.status] += 1

    return {
        "total_rows": len(rows_list),
        "by_status": by_status,
        "by_technique": dict(sorted(by_technique.items())),
    }


def stable_sort(rows: List[CoverageRow]) -> List[CoverageRow]:
    return sorted(rows, key=lambda r: (r.technique_id, r.control_id))


def render_markdown(rows: List[CoverageRow], summary: Dict[str, object]) -> str:
    by_status = summary["by_status"]
    by_technique = summary["by_technique"]

    lines: List[str] = []
    lines.append("# Coverage Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total rows: {summary['total_rows']}")
    lines.append(f"- Covered: {by_status['covered']}")
    lines.append(f"- Partial: {by_status['partial']}")
    lines.append(f"- Missing: {by_status['missing']}")
    lines.append("")
    lines.append("## By Technique")
    lines.append("")
    lines.append("| Technique | Covered | Partial | Missing |")
    lines.append("|---|---:|---:|---:|")
    for tech, counts in by_technique.items():
        lines.append(f"| {tech} | {counts['covered']} | {counts['partial']} | {counts['missing']} |")
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    lines.append("| Technique | Control | Status | Owner | Notes |")
    lines.append("|---|---|---|---|---|")
    for r in stable_sort(rows):
        # Keep markdown deterministic and safe; avoid pipes from notes.
        safe_notes = r.notes.replace("|", "/")
        lines.append(f"| {r.technique_id} | {r.control_id} | {r.status} | {r.owner} | {safe_notes} |")
    lines.append("")
    return "\n".join(lines)
