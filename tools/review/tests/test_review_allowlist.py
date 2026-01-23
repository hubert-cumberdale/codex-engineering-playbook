from __future__ import annotations

from tools.review import run_review_checks


def test_orchestrator_allowlist_contains_orchestrate() -> None:
    assert "tools/orchestrator/orchestrate.py" in run_review_checks.ORCHESTRATOR_ALLOWLIST


def test_check_scope_allows_orchestrator_path() -> None:
    changed_files = ["tools/orchestrator/orchestrate.py"]
    lines, hard_fail = run_review_checks.check_scope(changed_files)
    assert hard_fail is False
    assert any("[PASS] Orchestrator path allowlist" in line for line in lines)
