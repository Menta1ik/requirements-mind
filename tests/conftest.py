"""Shared fixtures for the Requirements Mind CLI tests.

`cli.py` uses relative paths (`projects/<name>/...`), so most tests
operate by swapping the CWD for a temporary directory.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Make the repo root importable (for `import cli`).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture()
def chdir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Makes a temporary folder the current working directory for the test."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def make_project(chdir_tmp: Path):
    """Creates a minimal `projects/<name>/` project structure and its state.json.

    Returns a factory: `make_project(name, status="intake")` → Path to the folder.
    """
    import cli  # noqa: WPS433 — deferred import, after chdir/sys.path

    def _factory(name: str, status: str = "intake", **overrides) -> Path:
        cli.ensure_project_dirs(name)
        state = cli.ProjectState(project=name, status=status, **overrides)
        cli.save_state(name, state)
        return chdir_tmp / "projects" / name

    return _factory
