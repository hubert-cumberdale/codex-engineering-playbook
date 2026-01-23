from __future__ import annotations

import os
from pathlib import Path

from tools.evidence import cli


def test_cli_index_silent_success(tmp_path: Path, capsys) -> None:
    root = tmp_path / ".orchestrator_logs"
    root.mkdir(parents=True, exist_ok=True)
    out_path = tmp_path / "evidence_index.json"

    # Use chdir to make repo_root stable for indexer.
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        rc = cli.run(["index", "--root", ".orchestrator_logs", "--out", str(out_path)])
    finally:
        os.chdir(cwd)

    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""
    assert out_path.is_file()
