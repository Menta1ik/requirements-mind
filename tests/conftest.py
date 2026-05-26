"""Общие фикстуры для тестов Requirements Mind CLI.

`cli.py` использует относительные пути (`projects/<name>/...`), поэтому
большинство тестов работают через подмену CWD на временную директорию.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Делаем корень репозитория импортируемым (для `import cli`).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture()
def chdir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Делает временную папку текущей рабочей директорией на время теста."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def make_project(chdir_tmp: Path):
    """Создаёт минимальную структуру проекта `projects/<name>/` и его state.json.

    Возвращает фабрику: `make_project(name, status="intake")` → Path к папке.
    """
    import cli  # noqa: WPS433 — отложенный импорт, после chdir/sys.path

    def _factory(name: str, status: str = "intake", **overrides) -> Path:
        cli.ensure_project_dirs(name)
        state = cli.ProjectState(project=name, status=status, **overrides)
        cli.save_state(name, state)
        return chdir_tmp / "projects" / name

    return _factory
