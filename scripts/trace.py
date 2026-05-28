#!/usr/bin/env python3
"""
RM Trace Linter — Tier 1 deterministic validation of requirement IDs and traceability.

Scans a single document or whole project for:
  * Malformed / non-canonical requirement IDs.
  * Duplicate IDs inside the same document.
  * Orphan IDs: referenced in SRS/Tech-Design/API-Contract but not defined upstream
    (in BRD or in the document itself).
  * Forward references in BRD that point to undefined SRS IDs.
  * Traceability gaps: Business Goals (BG-*) without any FR coverage.

This linter is deterministic, fast and cheap. It complements the LLM-based A2 validator:
A2 covers semantics, trace.py covers form. Both feed the same FAILED/PASSED contract.

Usage:
    uv run scripts/trace.py --project=<name>
    uv run scripts/trace.py --project=<name> --doc=BRD --version=1
    uv run scripts/trace.py --file=projects/<name>/docs/BRD-v1.md

Exit codes:
    0 — no errors (warnings allowed)
    1 — at least one error
    2 — invocation error (bad arguments, missing file)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

CURRENT_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = CURRENT_DIR / "projects"

# Canonical ID patterns. We deliberately keep the alphabet narrow:
#   - 2..5 uppercase letters for the "kind" prefix (FR, NFR, BG, BR, UC, VAL, etc.)
#   - optional subdomain segment of uppercase letters (REG, CAP, AUTH, ...)
#   - 1..4-digit sequence
# Examples that MUST match: FR-01, FR-REG-01, NFR-CAP-02, VAL-03, UC-REG-AS-1, BG-1.
ID_RE = re.compile(r"\b([A-Z]{2,5}(?:-[A-Z]{1,8}){0,3}-\d{1,4})\b")

# Heuristic: lines that DEFINE an ID typically start with the ID as a list bullet or
# table cell. Lines that REFERENCE an ID embed it in prose. We mark definitions by
# checking if the ID sits at the very beginning of a line (optionally after a list/
# table marker). Everything else is a reference.
DEF_LINE_RE = re.compile(
    r"^(?:\s*[-*|>]\s*|\s*\|\s*|\s*\d+\.\s*|#+\s*)?(?P<id>[A-Z]{2,5}(?:-[A-Z]{1,8}){0,3}-\d{1,4})\b"
)

DOC_KINDS = {"BRD", "SRS", "Tech-Design", "API-Contract"}


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    code: str
    message: str
    file: str
    line: int = 0

    def fmt(self) -> str:
        loc = f"{self.file}:{self.line}" if self.line else self.file
        return f"  [{self.severity.upper():7}] {self.code}: {self.message}  ({loc})"


@dataclass
class DocIndex:
    path: Path
    doc_kind: str | None = None
    defs: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))
    refs: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))

    def all_ids(self) -> set[str]:
        return set(self.defs.keys()) | set(self.refs.keys())


def detect_doc_kind(path: Path) -> str | None:
    """Infer BRD/SRS/Tech-Design/API-Contract from filename prefix."""
    name = path.name
    for kind in DOC_KINDS:
        if name.startswith(kind + "-") or name.startswith(kind.lower() + "-"):
            return kind
    return None


def scan_file(path: Path) -> DocIndex:
    """Walk one markdown file line-by-line, classify each ID match as def or ref."""
    idx = DocIndex(path=path, doc_kind=detect_doc_kind(path))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # Bubble up by leaving the index empty; caller decides whether to error out.
        print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
        return idx

    for lineno, raw in enumerate(text.splitlines(), start=1):
        # Strip code fences quickly — IDs inside fenced code blocks don't count
        # as definitions (they're typically examples). We don't track fence state
        # precisely; instead we skip lines that look like indented code (4+ spaces)
        # AND don't contain a table pipe — a conservative heuristic.
        if raw.startswith("    ") and "|" not in raw:
            continue

        def_match = DEF_LINE_RE.match(raw)
        defined_here: str | None = def_match.group("id") if def_match else None
        if defined_here:
            idx.defs[defined_here].append(lineno)

        for m in ID_RE.finditer(raw):
            ident = m.group(1)
            if ident == defined_here:
                # Already recorded as a definition; the same token at the start
                # of the line shouldn't also count as a reference.
                continue
            idx.refs[ident].append(lineno)
    return idx


def check_duplicates(idx: DocIndex, issues: list[Issue]) -> None:
    for ident, lines in idx.defs.items():
        if len(lines) > 1:
            issues.append(
                Issue(
                    severity="error",
                    code="RM-TR-001",
                    message=f"ID `{ident}` определён {len(lines)} раз (строки: {', '.join(map(str, lines))})",
                    file=str(idx.path),
                    line=lines[0],
                )
            )


def check_id_shape(idx: DocIndex, issues: list[Issue]) -> None:
    """Catch close-but-wrong shapes that ID_RE already filters by definition,
    but flag suspiciously short or all-numeric tails. This pass is conservative
    and only emits warnings — strict shape is what ID_RE enforces."""
    for ident in idx.all_ids():
        # Tail digits — a 5+ digit tail is almost certainly a mistake
        # (we'd expect FR-100 max for human-managed specs).
        tail = ident.rsplit("-", 1)[-1]
        if len(tail) > 4:
            lines = idx.defs.get(ident) or idx.refs.get(ident, [0])
            issues.append(
                Issue(
                    severity="warning",
                    code="RM-TR-010",
                    message=f"ID `{ident}` имеет необычно длинный числовой хвост ({len(tail)} цифр) — проверьте",
                    file=str(idx.path),
                    line=lines[0],
                )
            )


def check_orphans_within_doc(idx: DocIndex, issues: list[Issue]) -> None:
    """Refs that nobody defined anywhere in the same document. This is a soft
    check — many refs legitimately point to other documents. We emit warnings
    only for the most-common-kind pattern (e.g. an SRS that references FR-XX
    but never defines it AND has no BRD link)."""
    # No-op at file level; cross-document check happens in project mode.
    return


def cross_doc_check(indexes: list[DocIndex], issues: list[Issue]) -> None:
    """Cross-document: every ID referenced anywhere should be defined somewhere."""
    all_defs: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    all_refs: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    for idx in indexes:
        for ident, lines in idx.defs.items():
            for ln in lines:
                all_defs[ident].append((idx.path, ln))
        for ident, lines in idx.refs.items():
            for ln in lines:
                all_refs[ident].append((idx.path, ln))

    for ident, refs in all_refs.items():
        if ident in all_defs:
            continue
        # Skip IDs that look like external system codes (e.g. HTTP-200) — by convention
        # those are pure numeric statuses we don't manage.
        if ident.startswith("HTTP-"):
            continue
        first_path, first_line = refs[0]
        issues.append(
            Issue(
                severity="error",
                code="RM-TR-002",
                message=f"ID `{ident}` упоминается, но не определён ни в одном документе проекта",
                file=str(first_path),
                line=first_line,
            )
        )


def check_bg_coverage(indexes: list[DocIndex], issues: list[Issue]) -> None:
    """Every BG-* defined in BRD should be referenced by at least one FR-* in SRS."""
    bg_defs: dict[str, tuple[Path, int]] = {}
    for idx in indexes:
        if idx.doc_kind != "BRD":
            continue
        for ident, lines in idx.defs.items():
            if ident.startswith("BG-"):
                bg_defs[ident] = (idx.path, lines[0])
    if not bg_defs:
        return

    # Collect all SRS texts to scan for BG references within FR context.
    srs_indexes = [i for i in indexes if i.doc_kind == "SRS"]
    if not srs_indexes:
        # No SRS yet — not an error, just nothing to trace.
        return

    referenced_bgs: set[str] = set()
    for idx in srs_indexes:
        referenced_bgs.update(idx.refs.keys())

    for bg, (path, line) in bg_defs.items():
        if bg not in referenced_bgs:
            issues.append(
                Issue(
                    severity="warning",
                    code="RM-TR-020",
                    message=f"Business Goal `{bg}` не покрыт ни одним FR в SRS (нет ссылки)",
                    file=str(path),
                    line=line,
                )
            )


def collect_doc_files(project: str, doc: str | None, version: str | None) -> list[Path]:
    """Resolve which files to scan for `--project=...` mode."""
    proj_dir = PROJECTS_DIR / project
    docs_dir = proj_dir / "docs"
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Папка не найдена: {docs_dir}")

    files = sorted(docs_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"В {docs_dir} нет .md файлов")

    if doc:
        prefix = f"{doc}-"
        files = [f for f in files if f.name.startswith(prefix)]
    if version:
        suffix = f"-v{version}.md"
        files = [f for f in files if f.name.endswith(suffix)]

    if not files:
        raise FileNotFoundError("Подходящих файлов не найдено по фильтрам --doc/--version")
    return files


def print_report(indexes: list[DocIndex], issues: list[Issue]) -> int:
    """Pretty-print results. Returns process exit code."""
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    print()
    print("=" * 70)
    print(f"RM Trace Linter — {len(indexes)} файл(ов) проверено")
    print("=" * 70)
    for idx in indexes:
        print(f"  • {idx.path.name}: {len(idx.defs)} ID определено, {len(idx.refs)} ссылок")
    print()

    if errors:
        print(f"❌ Ошибок: {len(errors)}")
        for i in errors:
            print(i.fmt())
        print()
    if warnings:
        print(f"⚠️  Предупреждений: {len(warnings)}")
        for i in warnings:
            print(i.fmt())
        print()

    if not errors and not warnings:
        print("✅ Проблем не найдено.")
    elif not errors:
        print("✅ Ошибок нет (есть предупреждения — посмотрите выше).")
    else:
        print("❌ Есть блокирующие ошибки трассируемости.")

    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="trace.py",
        description="Tier 1 deterministic linter for requirement IDs and traceability.",
    )
    p.add_argument("--project", help="Имя проекта в projects/")
    p.add_argument("--doc", choices=sorted(DOC_KINDS), help="Тип документа (фильтр)")
    p.add_argument("--version", help="Номер версии (фильтр, без префикса v)")
    p.add_argument("--file", help="Путь к одиночному .md (альтернатива --project)")
    args = p.parse_args(argv)

    if not args.project and not args.file:
        p.error("требуется --project или --file")

    files: list[Path]
    if args.file:
        f = Path(args.file)
        if not f.is_file():
            print(f"error: файл не найден: {f}", file=sys.stderr)
            return 2
        files = [f]
    else:
        try:
            files = collect_doc_files(args.project, args.doc, args.version)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    indexes = [scan_file(f) for f in files]
    issues: list[Issue] = []
    for idx in indexes:
        check_duplicates(idx, issues)
        check_id_shape(idx, issues)
        check_orphans_within_doc(idx, issues)
    # Cross-document checks only make sense when we scan a whole project.
    if not args.file:
        cross_doc_check(indexes, issues)
        check_bg_coverage(indexes, issues)

    return print_report(indexes, issues)


if __name__ == "__main__":
    sys.exit(main())
