"""Tests for the FSM transitions in `handle_intake` and `handle_validate`.

Cover:
* explicit `rm_status: complete|incomplete` in context.md → drafting / needs_questions;
* substring fallback when there is no frontmatter (with a warning on stderr);
* `rm_verdict: PASSED|FAILED` in the validation report → approved / needs_revision;
* robustness against the words "FAILED" / "недостаточно" appearing in ordinary prose.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

import cli


# ---------- handle_intake ----------------------------------------------------


def _ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(**kw)


def test_intake_complete_via_frontmatter(make_project, chdir_tmp: Path) -> None:
    pdir = make_project("p1", status="intake")
    (pdir / "context.md").write_text(
        "---\nrm_status: complete\n---\n\n"
        "The body may contain the words 'недостаточно' and 'FAILED' — "
        "they must not affect the FSM.\n",
        encoding="utf-8",
    )

    cli.handle_intake(_ns(project="p1"))
    assert cli.load_state("p1").status == "drafting"


def test_intake_incomplete_via_frontmatter(make_project, chdir_tmp: Path) -> None:
    pdir = make_project("p2", status="intake")
    (pdir / "context.md").write_text(
        "---\nrm_status: incomplete\n---\n\n# Context\nClarifications are needed.\n",
        encoding="utf-8",
    )

    cli.handle_intake(_ns(project="p2"))
    assert cli.load_state("p2").status == "needs_questions"


def test_intake_fallback_substring_complete(make_project, chdir_tmp: Path, capsys) -> None:
    """No frontmatter and no trigger words — transition to drafting via fallback."""
    pdir = make_project("p3", status="intake")
    (pdir / "context.md").write_text("# Context\nAll good.\n", encoding="utf-8")

    cli.handle_intake(_ns(project="p3"))
    assert cli.load_state("p3").status == "drafting"
    captured = capsys.readouterr().out
    assert "frontmatter" in captured  # there must be a fallback warning


def test_intake_fallback_substring_incomplete(make_project, chdir_tmp: Path) -> None:
    pdir = make_project("p4", status="intake")
    # The Russian marker text is intentional: it exercises cli.py's legacy
    # back-compat substring fallback ("недостаточно" / "Флаг неполноты").
    (pdir / "context.md").write_text(
        "# Context\nДанных недостаточно, см. Флаг неполноты.\n",
        encoding="utf-8",
    )

    cli.handle_intake(_ns(project="p4"))
    assert cli.load_state("p4").status == "needs_questions"


def test_intake_missing_context_keeps_state(make_project, chdir_tmp: Path) -> None:
    make_project("p5", status="intake")
    cli.handle_intake(_ns(project="p5"))
    # context.md was not created — the status must not change.
    assert cli.load_state("p5").status == "intake"


# ---------- handle_validate --------------------------------------------------


def _seed_validate(make_project, name: str, report_body: str) -> Path:
    pdir = make_project(name, status="validating", document="BRD", iteration=1)
    (pdir / "messages" / "a2-to-a4-v1.md").write_text(report_body, encoding="utf-8")
    return pdir


def test_validate_passed_via_frontmatter(make_project, chdir_tmp: Path) -> None:
    _seed_validate(
        make_project,
        "v1",
        "---\nrm_verdict: PASSED\n---\n\n"
        "The report may contain the phrase 'FAILED is not acceptable' — it must not break the verdict.\n",
    )
    cli.handle_validate(_ns(project="v1", doc="BRD", version=1))
    assert cli.load_state("v1").status == "approved"


def test_validate_failed_via_frontmatter(make_project, chdir_tmp: Path) -> None:
    _seed_validate(
        make_project,
        "v2",
        "---\nrm_verdict: FAILED\n---\n\nNotes: ...\n",
    )
    cli.handle_validate(_ns(project="v2", doc="BRD", version=1))
    assert cli.load_state("v2").status == "needs_revision"


def test_validate_fallback_marker_failed(make_project, chdir_tmp: Path, capsys) -> None:
    """The narrow fallback catches only `**Вердикт:** FAILED`, not the bare word."""
    # The Russian marker `**Вердикт:** FAILED` is intentional: it exercises
    # cli.py's legacy back-compat fallback for the validation verdict.
    _seed_validate(
        make_project,
        "v3",
        "# Report\n**Вердикт:** FAILED\nNotes: ...\n",
    )
    cli.handle_validate(_ns(project="v3", doc="BRD", version=1))
    assert cli.load_state("v3").status == "needs_revision"
    assert "frontmatter" in capsys.readouterr().out


def test_validate_fallback_does_not_match_bare_failed_word(make_project, chdir_tmp: Path) -> None:
    """No frontmatter and no narrow marker — the report is treated as PASSED."""
    _seed_validate(
        make_project,
        "v4",
        "# Report\nFAILED is not acceptable as a phrasing here.\n",
    )
    cli.handle_validate(_ns(project="v4", doc="BRD", version=1))
    assert cli.load_state("v4").status == "approved"


def test_validate_missing_report_keeps_state(make_project, chdir_tmp: Path) -> None:
    make_project("v5", status="validating")
    cli.handle_validate(_ns(project="v5", doc="BRD", version=1))
    assert cli.load_state("v5").status == "validating"


# ---------- handle_reset -----------------------------------------------------


def test_reset_changes_status_with_yes(make_project, chdir_tmp: Path) -> None:
    make_project("r1", status="drafting")
    cli.handle_reset(_ns(project="r1", to="intake", yes=True))
    state = cli.load_state("r1")
    assert state.status == "intake"
    assert state.active_agents == ["a1"]


def test_reset_rejects_invalid_target(make_project, chdir_tmp: Path) -> None:
    make_project("r2", status="drafting")
    with pytest.raises(SystemExit) as exc:
        cli.handle_reset(_ns(project="r2", to="bogus", yes=True))
    assert exc.value.code == 2


def test_reset_noop_when_already_in_target(make_project, chdir_tmp: Path) -> None:
    make_project("r3", status="approved")
    cli.handle_reset(_ns(project="r3", to="approved", yes=True))
    assert cli.load_state("r3").status == "approved"
