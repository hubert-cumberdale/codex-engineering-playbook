from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
CONTENT_DIR = ROOT / "content"
OUT_ZIP = ART / "content_bundle.zip"

# Fixed timestamp for deterministic zip entries
FIXED_DT = (2000, 1, 1, 0, 0, 0)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in CONTENT_DIR.rglob("*") if p.is_file()])
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            rel = p.relative_to(ROOT).as_posix()
            data = p.read_bytes()
            info = zipfile.ZipInfo(rel)
            info.date_time = FIXED_DT
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)

    print("BUNDLE_WRITTEN artifacts/content_bundle.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
