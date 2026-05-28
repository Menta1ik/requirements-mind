"""Тесты Tier 1 линтера трассируемости (scripts/trace.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import trace as trace_mod  # noqa: E402  — после правки sys.path


# ---------- Юнит-тесты ID_RE и DEF_LINE_RE ----------

@pytest.mark.parametrize(
    "ident",
    [
        "FR-01",
        "FR-REG-01",
        "NFR-CAP-02",
        "VAL-03",
        "UC-REG-AS-1",
        "BG-1",
        "BR-12",
    ],
)
def test_id_regex_matches_canonical(ident: str) -> None:
    assert trace_mod.ID_RE.fullmatch(ident), f"должен матчиться: {ident}"


@pytest.mark.parametrize(
    "noise",
    [
        "fr-01",          # строчные
        "FR_01",          # подчёркивание вместо дефиса
        "F-01",           # короткий префикс (1 буква)
        "FRRRRRR-01",     # слишком длинный префикс (>5)
        "FR-",            # без хвоста
        "FR-01234567",    # слишком длинный хвост (>4) — игнорируется ID_RE (он матчит {1,4})
    ],
)
def test_id_regex_rejects_garbage(noise: str) -> None:
    # ID_RE может найти валидную подстроку внутри FR-01234567 (FR-0123), но
    # fullmatch должен отказать.
    assert not trace_mod.ID_RE.fullmatch(noise), f"не должен матчиться целиком: {noise}"


def test_def_line_matches_bullet() -> None:
    m = trace_mod.DEF_LINE_RE.match("- FR-REG-01: Регистрация пользователя")
    assert m and m.group("id") == "FR-REG-01"


def test_def_line_matches_table_cell() -> None:
    m = trace_mod.DEF_LINE_RE.match("| FR-01 | Описание | M |")
    assert m and m.group("id") == "FR-01"


def test_def_line_ignores_prose_reference() -> None:
    # Префикс "См. " — это явная ссылка, не определение.
    assert trace_mod.DEF_LINE_RE.match("См. FR-01 в SRS") is None


# ---------- Сканер файлов ----------

def test_scan_file_separates_defs_and_refs(tmp_path: Path) -> None:
    f = tmp_path / "SRS-v1.md"
    f.write_text(
        "# SRS\n"
        "- FR-01: первое требование\n"
        "- FR-02: ссылается на FR-01 и BG-1\n"
        "См. также NFR-CAP-02 ниже.\n"
        "- NFR-CAP-02: метрика производительности\n",
        encoding="utf-8",
    )
    idx = trace_mod.scan_file(f)
    assert set(idx.defs.keys()) == {"FR-01", "FR-02", "NFR-CAP-02"}
    # FR-01 и BG-1 встречаются как ссылки, NFR-CAP-02 в строке "См. также..."
    assert "FR-01" in idx.refs
    assert "BG-1" in idx.refs
    assert "NFR-CAP-02" in idx.refs


def test_scan_file_detects_doc_kind(tmp_path: Path) -> None:
    for name, expected in [
        ("BRD-v1.md", "BRD"),
        ("SRS-v2.md", "SRS"),
        ("Tech-Design-v1.md", "Tech-Design"),
        ("API-Contract-v3.md", "API-Contract"),
        ("notes.md", None),
    ]:
        f = tmp_path / name
        f.write_text("# stub", encoding="utf-8")
        idx = trace_mod.scan_file(f)
        assert idx.doc_kind == expected, f"{name} → {idx.doc_kind}"


# ---------- Проверки ----------

def test_duplicates_reported(tmp_path: Path) -> None:
    f = tmp_path / "SRS-v1.md"
    f.write_text(
        "- FR-01: первое\n- FR-01: дубликат\n",
        encoding="utf-8",
    )
    idx = trace_mod.scan_file(f)
    issues: list[trace_mod.Issue] = []
    trace_mod.check_duplicates(idx, issues)
    assert any(i.code == "RM-TR-001" for i in issues)


def test_cross_doc_orphan_reference(tmp_path: Path) -> None:
    brd = tmp_path / "BRD-v1.md"
    brd.write_text("- BG-1: цель\n", encoding="utf-8")
    srs = tmp_path / "SRS-v1.md"
    # FR-99 нигде не определён
    srs.write_text("- FR-01: покрывает BG-1\nСм. также FR-99 (TBD).\n", encoding="utf-8")

    indexes = [trace_mod.scan_file(brd), trace_mod.scan_file(srs)]
    issues: list[trace_mod.Issue] = []
    trace_mod.cross_doc_check(indexes, issues)
    assert any(i.code == "RM-TR-002" and "FR-99" in i.message for i in issues)


def test_bg_coverage_warns_when_no_fr_links_it(tmp_path: Path) -> None:
    brd = tmp_path / "BRD-v1.md"
    brd.write_text("- BG-1: покрыта\n- BG-2: сирота\n", encoding="utf-8")
    srs = tmp_path / "SRS-v1.md"
    srs.write_text("- FR-01: трассируется к BG-1\n", encoding="utf-8")

    indexes = [trace_mod.scan_file(brd), trace_mod.scan_file(srs)]
    issues: list[trace_mod.Issue] = []
    trace_mod.check_bg_coverage(indexes, issues)
    bg2 = [i for i in issues if "BG-2" in i.message]
    assert bg2 and bg2[0].severity == "warning" and bg2[0].code == "RM-TR-020"


def test_bg_coverage_silent_when_no_srs(tmp_path: Path) -> None:
    brd = tmp_path / "BRD-v1.md"
    brd.write_text("- BG-1: только BRD пока\n", encoding="utf-8")
    indexes = [trace_mod.scan_file(brd)]
    issues: list[trace_mod.Issue] = []
    trace_mod.check_bg_coverage(indexes, issues)
    assert issues == []


# ---------- E2E через main() ----------

def test_main_returns_zero_on_clean_file(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    f = tmp_path / "SRS-v1.md"
    f.write_text("- FR-01: хорошее требование\n", encoding="utf-8")
    rc = trace_mod.main(["--file", str(f)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "RM Trace Linter" in out


def test_main_returns_one_on_duplicate(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    f = tmp_path / "SRS-v1.md"
    f.write_text("- FR-01: a\n- FR-01: b\n", encoding="utf-8")
    rc = trace_mod.main(["--file", str(f)])
    assert rc == 1
    assert "RM-TR-001" in capsys.readouterr().out


def test_main_returns_two_on_missing_file(capsys: pytest.CaptureFixture) -> None:
    rc = trace_mod.main(["--file", "/nonexistent/path.md"])
    assert rc == 2


def test_main_project_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    # Подменяем PROJECTS_DIR в модуле, чтобы не требовать chdir.
    proj = tmp_path / "projects" / "demo"
    draft = proj / "draft"
    draft.mkdir(parents=True)
    (draft / "BRD-v1.md").write_text("- BG-1: цель\n", encoding="utf-8")
    (draft / "SRS-v1.md").write_text("- FR-01: покрывает BG-1\n", encoding="utf-8")

    monkeypatch.setattr(trace_mod, "PROJECTS_DIR", tmp_path / "projects")
    rc = trace_mod.main(["--project", "demo"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "2 файл(ов)" in out


def test_main_project_mode_scans_draft_and_final(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """Реальный сценарий: BRD утверждён (final/), SRS в работе (draft/).
    Линтер должен видеть оба и ловить orphan-ссылку из SRS на несуществующий FR."""
    proj = tmp_path / "projects" / "demo"
    (proj / "final").mkdir(parents=True)
    (proj / "draft").mkdir(parents=True)
    (proj / "final" / "BRD-v1-final.md").write_text("- BG-1: цель\n", encoding="utf-8")
    (proj / "draft" / "SRS-v1.md").write_text(
        "- FR-01: покрывает BG-1\nСм. также FR-42 (TBD).\n", encoding="utf-8"
    )

    monkeypatch.setattr(trace_mod, "PROJECTS_DIR", tmp_path / "projects")
    rc = trace_mod.main(["--project", "demo"])
    assert rc == 1  # orphan FR-42
    out = capsys.readouterr().out
    assert "2 файл(ов)" in out
    assert "FR-42" in out


def test_main_project_mode_filters_final_by_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--version=1` должен ловить и `-v1.md`, и `-v1-final.md`."""
    proj = tmp_path / "projects" / "demo"
    (proj / "draft").mkdir(parents=True)
    (proj / "final").mkdir(parents=True)
    (proj / "draft" / "BRD-v2.md").write_text("- BG-2: новая\n", encoding="utf-8")
    (proj / "final" / "BRD-v1-final.md").write_text("- BG-1: старая\n", encoding="utf-8")

    monkeypatch.setattr(trace_mod, "PROJECTS_DIR", tmp_path / "projects")
    files = trace_mod.collect_doc_files("demo", doc="BRD", version="1")
    assert len(files) == 1
    assert files[0].name == "BRD-v1-final.md"
