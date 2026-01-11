from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
INDEX = ART / "site" / "index.html"

HREF_RE = re.compile(r'href="(#.*?)"')


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    hrefs = sorted(set(HREF_RE.findall(html)))

    missing: list[str] = []
    for href in hrefs:
        anchor = href[1:]  # drop '#'
        if f"id='{anchor}'" not in html and f'id="{anchor}"' not in html:
            missing.append(href)

    report = {
        "taskpack_id": "TASK-1202-web-static-build-evidence",
        "checked_file": "artifacts/site/index.html",
        "hrefs": hrefs,
        "missing_anchors": missing,
        "status": "ok" if not missing else "failed",
    }

    ART.mkdir(parents=True, exist_ok=True)
    (ART / "link_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if missing:
        print("LINK_CHECK_FAILED", missing)
        return 1

    print("LINK_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
