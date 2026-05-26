"""Тесты на санитизацию имени проекта (`_validate_project_name`)."""
from __future__ import annotations

import pytest

import cli


@pytest.mark.parametrize(
    "name",
    ["my-app", "MyApp", "a", "project_1", "A_B-c-123", "x" * 64],
)
def test_accepts_valid_names(name: str) -> None:
    assert cli._validate_project_name(name) == name


@pytest.mark.parametrize(
    "name",
    [
        "../etc",          # path traversal
        "../../root",
        "a/b",             # slash
        "a\\b",            # backslash
        "my project",      # пробел
        "проект",          # кириллица
        "",                # пустая строка
        "x" * 65,          # за пределами длины
        ".hidden",         # точка в начале
        "name;rm -rf /",   # инъекция
    ],
)
def test_rejects_invalid_names(name: str) -> None:
    with pytest.raises(SystemExit) as exc:
        cli._validate_project_name(name)
    assert exc.value.code == 2
