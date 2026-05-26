"""Тесты для `cli._read_frontmatter` — мини-парсера YAML-блока в начале .md."""
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
    p = _write(tmp_path / "ctx.md", "# Просто заголовок\nrm_status: complete\n")
    # Первая строка — не `---`, значит frontmatter не распознан.
    assert cli._read_frontmatter(p) == {}


def test_missing_file_returns_empty(tmp_path: Path) -> None:
    assert cli._read_frontmatter(str(tmp_path / "nope.md")) == {}


def test_handles_quotes_and_whitespace(tmp_path: Path) -> None:
    p = _write(tmp_path / "ctx.md", '---\nrm_status: "Complete"\nname:   \'My-Proj\'\n---\n')
    fm = cli._read_frontmatter(p)
    assert fm["rm_status"] == "complete"
    assert fm["name"] == "my-proj"


def test_stops_at_closing_delimiter(tmp_path: Path) -> None:
    """Пары `key: value` после второго `---` не должны попадать в frontmatter."""
    p = _write(
        tmp_path / "ctx.md",
        "---\nrm_status: incomplete\n---\n\n## Раздел\nignored_key: should_not_leak\n",
    )
    fm = cli._read_frontmatter(p)
    assert fm == {"rm_status": "incomplete"}
    assert "ignored_key" not in fm
