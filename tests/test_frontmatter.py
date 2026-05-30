"""Tests for `cli._read_frontmatter` — the mini parser for the YAML block at the start of an .md."""
from __future__ import annotations

from pathlib import Path

import cli


def _write(path: Path, content: str) -> str:
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_reads_simple_frontmatter(tmp_path: Path) -> None:
    p = _write(tmp_path / "ctx.md", "---\nrm_status: complete\nfoo: BAR\n---\n\n# body\n")
    fm = cli._read_frontmatter(p)
    assert fm == {"rm_status": "complete", "foo": "bar"}


def test_no_frontmatter_returns_empty(tmp_path: Path) -> None:
    p = _write(tmp_path / "ctx.md", "# Just a heading\nrm_status: complete\n")
    # The first line is not `---`, so the frontmatter is not recognized.
    assert cli._read_frontmatter(p) == {}


def test_missing_file_returns_empty(tmp_path: Path) -> None:
    assert cli._read_frontmatter(str(tmp_path / "nope.md")) == {}


def test_handles_quotes_and_whitespace(tmp_path: Path) -> None:
    p = _write(tmp_path / "ctx.md", '---\nrm_status: "Complete"\nname:   \'My-Proj\'\n---\n')
    fm = cli._read_frontmatter(p)
    assert fm["rm_status"] == "complete"
    assert fm["name"] == "my-proj"


def test_stops_at_closing_delimiter(tmp_path: Path) -> None:
    """`key: value` pairs after the second `---` must not leak into the frontmatter."""
    p = _write(
        tmp_path / "ctx.md",
        "---\nrm_status: incomplete\n---\n\n## Section\nignored_key: should_not_leak\n",
    )
    fm = cli._read_frontmatter(p)
    assert fm == {"rm_status": "incomplete"}
    assert "ignored_key" not in fm
