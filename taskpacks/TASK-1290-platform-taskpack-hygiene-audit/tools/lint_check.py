from __future__ import annotations
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_LINE = 120

def main() -> int:
    failures = []
    for p in (ROOT / "tools").rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        if "\t" in text:
            failures.append(f"{p}: contains tabs")
        if not text.endswith("\n"):
            failures.append(f"{p}: missing trailing newline")
        for i, line in enumerate(text.splitlines(), start=1):
            if len(line) > MAX_LINE:
                failures.append(f"{p}: line {i} > {MAX_LINE}")

    if failures:
        print("LINT_CHECK_FAILED")
        for f in failures:
            print(f"- {f}")
        return 1

    print("LINT_CHECK_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
