from __future__ import annotations

import sys
from pathlib import Path


def _add_solution_src_to_syspath() -> None:
    # tests/ -> detection-strategy-generator/ -> src/
    here = Path(__file__).resolve()
    src_dir = here.parent.parent / "src"
    sys.path.insert(0, str(src_dir))


_add_solution_src_to_syspath()
