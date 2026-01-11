from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
SITE_OUT = ART / "site"
CONTENT = ROOT / "site" / "content.md"
TEMPLATE = ROOT / "site" / "template.html"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def md_to_html(md: str) -> str:
    # Minimal, deterministic “markdown-ish” transform:
    # - headings -> <h1>/<h2>
    # - blank lines preserved as paragraph breaks
    # - simple [text](#anchor) -> <a href="#anchor">text</a>
    lines = md.splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("# "):
            out.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2 id='{line[3:].strip().lower()}'>{line[3:].strip()}</h2>")
        elif line.strip().startswith("- "):
            out.append(f"<li>{line.strip()[2:]}</li>")
        elif line.strip() == "":
            out.append("")
        else:
            out.append(f"<p>{line}</p>")

    html = "\n".join(out)
    html = html.replace("[About](#about)", "<a href=\"#about\">About</a>")
    html = html.replace("[Evidence](#evidence)", "<a href=\"#evidence\">Evidence</a>")
    return html


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    SITE_OUT.mkdir(parents=True, exist_ok=True)

    md = CONTENT.read_text(encoding="utf-8")
    tmpl = TEMPLATE.read_text(encoding="utf-8")

    body = md_to_html(md)
    html = tmpl.replace("{{TITLE}}", "Mini Site").replace("{{BODY}}", body)

    out_path = SITE_OUT / "index.html"
    out_path.write_text(html + "\n", encoding="utf-8")

    manifest = {
        "taskpack_id": "TASK-1202-web-static-build-evidence",
        "inputs": {
            "content_md_sha256": sha256_text(md),
            "template_html_sha256": sha256_text(tmpl),
        },
        "outputs": {
            "index_html_sha256": sha256_text(html),
            "index_html_path": "artifacts/site/index.html",
        },
    }

    (ART / "build_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("SITE_BUILT artifacts/site/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
