from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "events.json"
ART = ROOT / "artifacts"


def fail(msg: str) -> None:
    raise ValueError(msg)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail("events.json must be a list")

    ids: set[str] = set()
    for idx, ev in enumerate(data):
        if not isinstance(ev, dict):
            fail(f"event[{idx}] must be an object")
        for key in ("id", "title", "choices"):
            if key not in ev:
                fail(f"event[{idx}] missing '{key}'")

        ev_id = ev["id"]
        if not isinstance(ev_id, str) or not ev_id:
            fail(f"event[{idx}].id must be non-empty string")
        if ev_id in ids:
            fail(f"duplicate event id: {ev_id}")
        ids.add(ev_id)

        choices = ev["choices"]
        if not isinstance(choices, list) or not choices:
            fail(f"event[{idx}].choices must be non-empty list")

        for cidx, ch in enumerate(choices):
            if not isinstance(ch, dict):
                fail(f"event[{idx}].choices[{cidx}] must be an object")
            if "text" not in ch or "next_id" not in ch:
                fail(f"event[{idx}].choices[{cidx}] requires text and next_id")
            if not isinstance(ch["text"], str) or not ch["text"]:
                fail(f"event[{idx}].choices[{cidx}].text must be non-empty string")
            nxt = ch["next_id"]
            if nxt is not None and (not isinstance(nxt, str) or not nxt):
                fail(f"event[{idx}].choices[{cidx}].next_id must be string or null")

    # Referential integrity
    broken: list[str] = []
    for ev in data:
        for ch in ev["choices"]:
            nxt = ch["next_id"]
            if nxt is not None and nxt not in ids:
                broken.append(f"{ev['id']} -> {nxt}")

    report = {
        "taskpack_id": "TASK-1203-game-content-validate-bundle",
        "file": "content/events.json",
        "event_count": len(data),
        "unique_ids": len(ids),
        "broken_links": broken,
        "status": "ok" if not broken else "failed",
    }

    (ART / "validation_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if broken:
        print("CONTENT_VALIDATION_FAILED", broken)
        return 1

    print("CONTENT_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
