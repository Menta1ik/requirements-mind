#!/usr/bin/env python3
import os
import re
import sys
import json
import shutil
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

console = Console()

# =====================================================================
# Хелперы: валидация имени проекта и парсинг frontmatter
# =====================================================================

_PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _validate_project_name(name: str) -> str:
    """Проверяет, что имя проекта безопасно для использования в путях ФС.

    Разрешает только латиницу, цифры, дефис и подчёркивание; длина 1-64.
    Это закрывает попытки path traversal через --project=../../etc и т. п.
    """
    if not _PROJECT_NAME_RE.match(name or ""):
        console.print(
            f"[red]❌ Недопустимое имя проекта: {name!r}.[/red]\n"
            f"[white]Разрешены символы [bold][A-Za-z0-9_-][/bold], длина 1-64.[/white]"
        )
        sys.exit(2)
    return name


def _read_frontmatter(path: str) -> Dict[str, Any]:
    """Читает YAML-подобный frontmatter из начала Markdown-файла.

    Поддерживается минимальный формат:
        ---
        key1: value1
        key2: value2
        ---
    Возвращает dict из строковых пар (значения lower-cased, обрезанные).
    Если frontmatter отсутствует или файл нечитаем — возвращает пустой dict.
    Целенаправленно без зависимости от PyYAML: frontmatter в Requirements Mind
    содержит плоские пары `key: value` и не требует полного YAML.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            head = f.read(4096)
    except OSError:
        return {}

    lines = head.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm: Dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip().lower()] = value.strip().strip('"').strip("'").lower()
    return fm

class ProjectState(BaseModel):
    project: str
    mode: str = "draft"  # draft / analyze
    document: str = "BRD"  # BRD / SRS / Tech-Design / API-Contract
    profile: Optional[int] = None  # 1-6 в соответствии с целевыми профилями проектов требований
    iteration: int = 1
    status: str = "onboarding"  # onboarding / intake / needs_questions / drafting / validating / needs_revision / approved
    active_agents: List[str] = ["a0"]
    open_questions: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

def get_project_dir(project_name: str) -> str:
    return os.path.join("projects", project_name)

def ensure_project_dirs(project_name: str):
    base_dir = get_project_dir(project_name)
    subdirs = ["input", "messages", "draft", "validation", "analysis", "final"]
    for subdir in subdirs:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
    
    # Создаем шаблоны файлов в input, если папка пуста
    input_dir = os.path.join(base_dir, "input")
    if not os.listdir(input_dir):
        with open(os.path.join(input_dir, "transcript.md"), "w", encoding="utf-8") as f:
            f.write("# Транскрипт встречи\n\n*(Вставьте сюда транскрипт обсуждения проекта)*\n")
        with open(os.path.join(input_dir, "requirements.md"), "w", encoding="utf-8") as f:
            f.write("# Первичные требования\n\n*(Вставьте сюда сырые требования или тикеты)*\n")

def load_state(project_name: str) -> ProjectState:
    state_path = os.path.join(get_project_dir(project_name), "state.json")
    if not os.path.exists(state_path):
        ensure_project_dirs(project_name)
        state = ProjectState(project=project_name)
        save_state(project_name, state)
        return state
    with open(state_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return ProjectState(**data)

def load_state_safe(project_name: str) -> Optional[ProjectState]:
    state_path = os.path.join(get_project_dir(project_name), "state.json")
    if not os.path.exists(state_path):
        return None
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ProjectState(**data)
    except Exception:
        return None

def save_state(project_name: str, state: ProjectState):
    state.last_updated = datetime.now().isoformat()
    state_path = os.path.join(get_project_dir(project_name), "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state.model_dump(), f, indent=2, ensure_ascii=False)

# =====================================================================
# Логика Команд CLI
# =====================================================================

def handle_init(args):
    project = _validate_project_name(args.project)
    ensure_project_dirs(project)
    state = load_state(project)
    
    console.print(Panel.fit(
        f"[bold green]Успешно инициализирован проект: {project}[/bold green]\n"
        f"📁 Путь: [cyan]{get_project_dir(project)}[/cyan]\n"
        f"⚙️ Текущий статус: [yellow]{state.status}[/yellow]\n\n"
        f"[bold white]Следующий шаг:[/bold white]\n"
        f"1. Попросите ИИ-ассистента в вашей IDE (Cursor, Claude Code, Antigravity, Codex) запустить онбординг:\n"
        f"   [yellow]«Мэри, давай запустим онбординг (RMONB) для нового проекта {project}»[/yellow]\n"
        f"2. После проведения онбординг-интервью и подготовки сырых файлов в input/ зафиксируйте это в CLI:\n"
        f"   [yellow]uv run cli.py onboard --project={project}[/yellow]",
        title="[bold]Requirements Mind — Инициализация[/bold]"
    ))

def handle_onboard(args):
    project = _validate_project_name(args.project)
    state = load_state(project)
    if state.status != "onboarding":
        console.print(f"[yellow]⚠️ Проект {project} уже прошел стадию онбординга (текущий статус: {state.status}).[/yellow]")
        return
    
    state.status = "intake"
    state.active_agents = ["a1"]
    save_state(project, state)
    
    console.print(Panel(
        f"[green]🎉 Онбординг проекта [bold]{project}[/bold] успешно завершен![/green]\n\n"
        f"Статус проекта изменен на: [yellow]intake[/yellow] (готов к анализу требований).\n\n"
        f"[bold white]ЧТО ДЕЛАТЬ ДАЛЬШЕ:[/bold white]\n"
        f"1. Убедитесь, что сырые файлы требований лежат в [cyan]projects/{project}/input/[/cyan]\n"
        f"2. Попросите ИИ-ассистента в вашей IDE запустить Intake-анализ:\n"
        f"   [yellow]«Запусти навык a1-intake-analyst для проекта {project} и создай context.md»[/yellow]\n"
        f"3. После завершения анализа зафиксируйте статус в терминале:\n"
        f"   [cyan]uv run cli.py intake --project={project}[/cyan]",
        title=" Requirements Mind Onboarding ",
        border_style="green"
    ))

def handle_intake(args):
    project = _validate_project_name(args.project)
    state = load_state(project)
    project_dir = get_project_dir(project)
    context_path = os.path.join(project_dir, "context.md")

    if not os.path.exists(context_path):
        console.print(Panel(
            f"[red]❌ Ошибка: Файл [bold]context.md[/bold] не найден по пути {context_path}[/red]\n\n"
            f"[bold white]Как исправить:[/bold white]\n"
            f"Попросите вашего ИИ-ассистента в IDE (например, Cursor или Claude Code) запустить навык [cyan]a1-intake-analyst[/cyan] из папки [cyan]skills/rm/[/cyan], чтобы проанализировать файлы в [cyan]input/[/cyan] и записать [cyan]context.md[/cyan].\n"
            f"После того как ИИ сгенерирует файл, запустите эту команду еще раз.",
            title="Ошибка: Отсутствует context.md"
        ))
        return

    # Управляющий сигнал — явный frontmatter `rm_status: complete|incomplete`.
    # Substring-match по свободному тексту оставлен только как fallback для
    # обратной совместимости (контексты, написанные до v2.1).
    fm = _read_frontmatter(context_path)
    if "rm_status" in fm:
        has_gaps = fm["rm_status"] != "complete"
    else:
        with open(context_path, "r", encoding="utf-8") as f:
            context_content = f.read()
        has_gaps = "Флаг неполноты" in context_content or "недостаточно" in context_content.lower()
        console.print(
            "[yellow]⚠️ В context.md отсутствует frontmatter `rm_status`. "
            "Используется устаревший substring-fallback. "
            "Попросите ИИ-агента A1 добавить frontmatter `rm_status: complete|incomplete` в начало файла.[/yellow]"
        )
    
    if has_gaps:
        state.status = "needs_questions"
        state.active_agents = ["a3"]
        save_state(project, state)
        console.print(Panel(
            f"[yellow]⚠️ Обнаружен флаг неполноты требований в context.md![/yellow]\n\n"
            f"[bold white]Следующий шаг:[/bold white]\n"
            f"1. Попросите вашего ИИ-ассистента в IDE запустить навык [cyan]a3-question-generator[/cyan] для генерации уточняющих вопросов в [cyan]questions.md[/cyan].\n"
            f"2. Ответьте на вопросы и сохраните их в [cyan]qa-history.md[/cyan].\n"
            f"3. Снова попросите ИИ обновить [cyan]context.md[/cyan], удалив флаг неполноты, и перезапустите: [yellow]uv run cli.py intake --project={project}[/yellow]",
            title="Требования неполные"
        ))
    else:
        state.status = "drafting"
        state.active_agents = ["a4"]
        save_state(project, state)
        console.print(Panel(
            f"[green]✅ context.md успешно проверен и зафиксирован![/green]\n"
            f"⚙️ Новый статус проекта: [yellow]{state.status}[/yellow] (готов к созданию черновика)\n\n"
            f"[bold white]Следующий шаг:[/bold white]\n"
            f"Попросите ИИ-ассистента в IDE запустить навык [cyan]a4-document-writer[/cyan] для генерации первого черновика [cyan]draft/{state.document}-v{state.iteration}.md[/cyan] по чеклистам базы знаний.\n"
            f"После генерации выполните команду: [yellow]uv run cli.py draft --project={project} --doc={state.document}[/yellow]",
            title="Контекст готов"
        ))

def handle_draft(args):
    project = _validate_project_name(args.project)
    doc = args.doc
    state = load_state(project)
    project_dir = get_project_dir(project)
    draft_file = f"{doc}-v{state.iteration}.md"
    draft_path = os.path.join(project_dir, "draft", draft_file)
    
    if not os.path.exists(draft_path):
        console.print(Panel(
            f"[red]❌ Ошибка: Файл черновика [bold]{draft_file}[/bold] не найден по пути {draft_path}[/red]\n\n"
            f"[bold white]Как исправить:[/bold white]\n"
            f"Попросите вашего ИИ-ассистента в IDE запустить навык [cyan]a4-document-writer[/cyan] для написания документа [cyan]{doc}[/cyan] и сохранения его по пути [cyan]draft/{draft_file}[/cyan].\n"
            f"После генерации файла запустите эту команду еще раз.",
            title="Черновик не найден"
        ))
        return
        
    state.status = "validating"
    state.active_agents = ["a2"]
    state.document = doc
    save_state(project, state)
    
    console.print(Panel(
        f"[green]✅ Черновик {draft_file} успешно обнаружен и зафиксирован![/green]\n"
        f"⚙️ Новый статус проекта: [yellow]{state.status}[/yellow] (готов к валидации)\n\n"
        f"[bold white]Следующий шаг:[/bold white]\n"
        f"Попросите ИИ-ассистента в IDE запустить навык [cyan]a2-requirements-validator[/cyan] для проверки качества черновика и сохранения отчета в [cyan]messages/a2-to-a4-v{state.iteration}.md[/cyan].\n"
        f"После прохождения валидации выполните: [yellow]uv run cli.py validate --project={project} --doc={doc} --version={state.iteration}[/yellow]",
        title="Черновик зафиксирован"
    ))

def handle_validate(args):
    project = _validate_project_name(args.project)
    doc = args.doc
    version = args.version
    state = load_state(project)
    project_dir = get_project_dir(project)
    report_file = f"a2-to-a4-v{version}.md"
    report_path = os.path.join(project_dir, "messages", report_file)

    if not os.path.exists(report_path):
        console.print(Panel(
            f"[red]❌ Ошибка: Отчет по валидации [bold]{report_file}[/bold] не найден в папке messages/[/red]\n\n"
            f"[bold white]Как исправить:[/bold white]\n"
            f"Попросите вашего ИИ-ассистента в IDE запустить навык [cyan]a2-requirements-validator[/cyan] для проверки черновика [cyan]{doc}-v{version}.md[/cyan].\n"
            f"ИИ должен проанализировать черновик по чеклистам и записать отчет в [cyan]messages/{report_file}[/cyan].\n"
            f"После этого запустите команду validate еще раз.",
            title="Отчет не найден"
        ))
        return

    # Управляющий сигнал — явный frontmatter `rm_verdict: passed|failed`.
    # Fallback — узкий маркер `**Вердикт:** FAILED` (а не голое "FAILED",
    # которое срабатывает на безобидные фразы вроде "FAILED is not acceptable").
    fm = _read_frontmatter(report_path)
    if "rm_verdict" in fm:
        is_failed = fm["rm_verdict"] != "passed"
    else:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        is_failed = "**Вердикт:** FAILED" in report_content or "**Verdict:** FAILED" in report_content
        console.print(
            "[yellow]⚠️ В отчёте отсутствует frontmatter `rm_verdict`. "
            "Используется устаревший маркер `**Вердикт:** FAILED`. "
            "Попросите ИИ-агента A2 добавить frontmatter `rm_verdict: PASSED|FAILED` в начало отчёта.[/yellow]"
        )
    
    if is_failed:
        state.status = "needs_revision"
        state.active_agents = ["a4"]
        save_state(project, state)
        console.print(Panel(
            f"[bold red]❌ Валидация не пройдена (FAILED) для версии v{version}![/bold red]\n"
            f"Отчет сохранен in [cyan]messages/{report_file}[/cyan]\n\n"
            f"[bold white]Следующий шаг:[/bold white]\n"
            f"1. Попросите ИИ-ассистента в IDE запустить навык [cyan]a4-document-writer[/cyan] для исправления документа на основе замечаний из отчета.\n"
            f"2. ИИ должен сохранить исправленный документ как [cyan]draft/{doc}-v{version}.md[/cyan] (или инкрементировать версию).\n"
            f"3. После исправления перезапустите команду validate.",
            title="Валидация FAILED"
        ))
    else:
        state.status = "approved"
        state.active_agents = ["master-orchestrator"]
        save_state(project, state)
        console.print(Panel(
            f"[bold green]✅ Валидация успешно пройдена (PASSED) для версии v{version}![/bold green]\n\n"
            f"[bold white]Следующий шаг:[/bold white]\n"
            f"Запустите команду утверждения и финализации документа:\n"
            f"[yellow]uv run cli.py final --project={project} --doc={doc} --version={version}[/yellow]",
            title="Валидация PASSED"
        ))

def handle_final(args):
    project = _validate_project_name(args.project)
    doc = args.doc
    version = args.version
    state = load_state(project)
    project_dir = get_project_dir(project)
    
    draft_file = f"{doc}-v{version}.md"
    draft_path = os.path.join(project_dir, "draft", draft_file)
    
    if not os.path.exists(draft_path):
        console.print(f"[red]❌ Ошибка: Черновик {draft_file} не найден.[/red]")
        return
        
    final_file = f"{doc}-v{version}-final.md"
    final_path = os.path.join(project_dir, "final", final_file)
    
    try:
        shutil.copy2(draft_path, final_path)
    except Exception as e:
        console.print(f"[red]❌ Ошибка копирования файла в final: {e}[/red]")
        return
        
    # Создаем лог оркестратора
    decision_path = os.path.join(project_dir, "messages", "orchestrator-decision.md")
    decision_text = (
        f"# Решение Оркестратора о финализации\n\n"
        f"* **Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"* **Проект:** {project}\n"
        f"* **Документ:** {doc}\n"
        f"* **Утвержденная версия:** v{version}\n\n"
        f"Документ успешно прошел валидацию и перенесен в папку финальных спецификаций: `final/{final_file}`.\n"
    )
    with open(decision_path, "w", encoding="utf-8") as f:
        f.write(decision_text)
        
    # Сдвигаем цепочку иерархии вперед: BRD -> SRS -> Tech-Design -> API-Contract
    hierarchy = ["BRD", "SRS", "Tech-Design", "API-Contract"]
    try:
        curr_idx = hierarchy.index(doc)
        if curr_idx < len(hierarchy) - 1:
            next_doc = hierarchy[curr_idx + 1]
            state.document = next_doc
            state.status = "intake"
            state.active_agents = ["a1"]
            state.iteration = 1
            next_step_msg = f"Цепочка сдвинута к следующему документу: [bold yellow]{next_doc}[/bold yellow]."
        else:
            state.status = "approved"
            state.active_agents = []
            next_step_msg = "🎉 Поздравляем! Полная цепочка спецификаций BRD → SRS → Tech Design → API Contract успешно разработана!"
    except ValueError:
        state.status = "approved"
        next_step_msg = "Спецификация успешно завершена."
        
    save_state(project, state)
    
    console.print(Panel(
        f"[green]🎉 Успешно финализирована спецификация: {doc}[/green]\n"
        f"📁 Файл сохранен: [cyan]final/{final_file}[/cyan]\n"
        f"⚖️ Решение записано в [cyan]messages/orchestrator-decision.md[/cyan]\n\n"
        f"[bold white]Следующий статус проекта:[/bold white] {state.status}\n"
        f"{next_step_msg}",
        title="Финализация завершена"
    ))

def handle_augment(args):
    """Запускает augment-режим: baseline-документ + артефакты → дополненная версия.

    Команда:
      1) копирует baseline в projects/<name>/input/baseline/<filename>,
      2) пишет/обновляет context.md с frontmatter rm_mode: augment + baseline_doc.*,
      3) переводит state.json в status=drafting, mode=augment, document=<doc>,
      4) выводит инструкцию для ИИ-ассистента запустить A1 → A4 в защищённом режиме.

    Контракт augment-режима описан в:
      - flows/09-augment.md
      - skills/rm/a4-document-writer.md (блок «Режим Augment»)
      - skills/rm/a1-intake-analyst.md (различение baseline vs artifacts)
      - skills/rm/master-orchestrator.md (контроль соблюдения контракта)
    """
    project = _validate_project_name(args.project)
    baseline_arg = args.baseline
    doc = args.doc

    # 1. Проверки на входе
    allowed_docs = {"BRD", "SRS", "Tech-Design", "API-Contract"}
    if doc not in allowed_docs:
        console.print(
            f"[red]❌ Недопустимый тип документа: {doc!r}.[/red]\n"
            f"Разрешены: {', '.join(sorted(allowed_docs))}."
        )
        sys.exit(2)

    if not os.path.isfile(baseline_arg):
        console.print(f"[red]❌ Baseline-файл не найден: {baseline_arg}[/red]")
        sys.exit(2)

    # 2. Подготовка папок и копирование baseline
    ensure_project_dirs(project)
    project_dir = get_project_dir(project)
    baseline_dir = os.path.join(project_dir, "input", "baseline")
    os.makedirs(baseline_dir, exist_ok=True)

    baseline_filename = os.path.basename(baseline_arg)
    baseline_dest = os.path.join(baseline_dir, baseline_filename)
    baseline_rel = os.path.join("input", "baseline", baseline_filename)

    # Не копируем сам в себя, если пользователь уже положил файл в input/baseline/
    if os.path.abspath(baseline_arg) != os.path.abspath(baseline_dest):
        shutil.copy2(baseline_arg, baseline_dest)

    # 3. Обновляем/создаём context.md с frontmatter augment
    today = datetime.now().strftime("%Y-%m-%d")
    context_path = os.path.join(project_dir, "context.md")
    augment_frontmatter = (
        "---\n"
        "rm_status: incomplete\n"
        f"updated_at: {today}\n"
        "rm_mode: augment\n"
        "baseline_doc:\n"
        f"  path: {baseline_rel}\n"
        f"  type: {doc}\n"
        "  preserve_structure: true\n"
        "---\n"
    )

    if os.path.exists(context_path):
        # Сохраняем существующий контент, заменяем только frontmatter
        with open(context_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing.startswith("---"):
            # Срезаем старый frontmatter
            end = existing.find("\n---", 3)
            if end != -1:
                body = existing[end + 4 :].lstrip("\n")
            else:
                body = existing  # некорректный frontmatter, не трогаем
        else:
            body = existing
        new_context = augment_frontmatter + "\n" + body
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(new_context)
        context_action = "обновлён"
    else:
        starter_body = (
            "# 🎯 Vision и бизнес-цели\n\n*(A1 заполнит из артефактов)*\n\n"
            "# 👥 Стейкхолдеры\n\n*(A1 заполнит из артефактов)*\n\n"
            "# ⚡ Ограничения\n\n*(A1 заполнит из артефактов)*\n\n"
            "## 🔄 Дельта для дополнения baseline\n\n"
            f"*(A1 опишет здесь: что нового пришло из артефактов и где встроить в `{baseline_rel}`)*\n\n"
            "## ❓ Открытые вопросы и пробелы\n\n"
            "*(A1 / A3 ведут реестр здесь)*\n"
        )
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(augment_frontmatter + "\n" + starter_body)
        context_action = "создан"

    # 4. Обновляем state.json
    state = load_state(project)
    state.mode = "augment"
    state.document = doc
    state.status = "drafting"
    state.active_agents = ["a1"]  # сначала A1 разберёт артефакты под augment
    save_state(project, state)

    # 5. Инструкция пользователю
    console.print(Panel(
        f"[green]🛡️  Augment-режим активирован для проекта [bold]{project}[/bold][/green]\n\n"
        f"📄 Baseline: [cyan]{baseline_rel}[/cyan]  (тип: {doc})\n"
        f"📝 context.md {context_action} с frontmatter [yellow]rm_mode: augment[/yellow]\n"
        f"⚙️  state.json: status=[yellow]drafting[/yellow], mode=[yellow]augment[/yellow]\n\n"
        f"[bold white]Что делать дальше:[/bold white]\n"
        f"1. Положите остальные артефакты (транскрипты, заметки, новые BR) в [cyan]projects/{project}/input/[/cyan] "
        f"(НЕ в подпапку baseline/).\n"
        f"2. Попросите ИИ-ассистента в IDE:\n"
        f"   [yellow]«Запусти a1-intake-analyst для проекта {project}. "
        f"Это augment-режим, baseline — {baseline_rel}, не растворяй его в context.md, "
        f"опиши только дельту из артефактов»[/yellow]\n"
        f"3. После того как A1 запишет context.md и context-changelog.md — зафиксируйте:\n"
        f"   [cyan]uv run cli.py intake --project={project}[/cyan]\n"
        f"4. Затем попросите ИИ запустить [cyan]a4-document-writer[/cyan]. "
        f"Он обязан показать diff-план в чате и дождаться вашего OK прежде, чем записывать "
        f"[cyan]draft/{doc}-v<N>.md[/cyan].\n\n"
        f"[dim]Контракт защиты baseline описан в flows/09-augment.md.[/dim]",
        title="Requirements Mind — Augment Mode",
        border_style="cyan"
    ))


def handle_analyze(args):
    project = _validate_project_name(args.project)
    task = args.task
    state = load_state(project)
    
    state.mode = "analyze"
    state.status = "drafting"
    state.active_agents = ["a6"]
    save_state(project, state)
    
    console.print(Panel(
        f"[cyan]📈 Зафиксирована аналитическая задача: \"{task}\"[/cyan]\n\n"
        f"[bold white]Как выполнить анализ:[/bold white]\n"
        f"1. Откройте диалог с вашим ИИ-ассистентом в IDE.\n"
        f"2. Попросите ИИ запустить навык [cyan]a6-analysis-writer[/cyan] для выполнения задачи: [yellow]\"{task}\"[/yellow].\n"
        f"3. ИИ проанализирует контекст проекта и запишет отчет в [cyan]analysis/analysis-vN.md[/cyan].",
        title="Режим B — Аналитическая сессия"
    ))

def handle_collaborate(args):
    project = _validate_project_name(args.project)
    agents = args.agents
    state = load_state(project)
    agents_list = [a.strip() for a in agents.split(",")]

    console.print(Panel(
        f"[bold yellow]👥 Настройка мультиагентного круглого стола (Party Mode) для проекта: {project}[/bold yellow]\n\n"
        f"[bold white]Инструкция для запуска обсуждения:[/bold white]\n"
        f"1. Откройте чат с вашим ИИ-ассистентом в IDE.\n"
        f"2. Попросите ИИ запустить навык [cyan]bmad-party-mode[/cyan] (из папки [cyan]skills/bmad/[/cyan]) со следующей инструкцией:\n"
        f"   [green]\"Запусти круглый стол между агентами {', '.join(agents_list)} для обсуждения следующей проблемы: ...\"[/green]\n"
        f"3. ИИ-ассистент выступит оркестратором, вызовет независимых агентов и запишет лог межагентного общения в файлы [cyan]messages/collaborate-*.md[/cyan].",
        title="Запуск Party Mode"
    ))

def handle_sync_vault(args):
    console.print("[cyan]🔄 Запуск скрипта синхронизации с Obsidian Vault...[/cyan]")
    import subprocess
    try:
        # sys.executable вместо "python3" — на Windows интерпретатор обычно "python",
        # а sys.executable указывает на активный venv в любой ОС.
        res = subprocess.run([sys.executable, "scripts/sync_to_vault.py"], capture_output=True, text=True)
        if res.returncode == 0:
            console.print("[green]✅ Синхронизация с Obsidian выполнена успешно.[/green]")
        else:
            console.print(f"[red]❌ Ошибка при синхронизации: {res.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Не удалось запустить скрипт синхронизации: {e}[/red]")

def handle_export_notebooklm(args):
    project = _validate_project_name(args.project)
    console.print(f"[cyan]📤 Запуск подготовки экспорта для NotebookLM проекта {project}...[/cyan]")
    import subprocess
    try:
        # sys.executable вместо "python3" — на Windows интерпретатор обычно "python".
        res = subprocess.run([sys.executable, "scripts/export_to_notebooklm.py", "--project", project], capture_output=True, text=True)
        if res.returncode == 0:
            console.print("[green]✅ Экспорт для NotebookLM подготовлен.[/green]")
        else:
            console.print(f"[red]❌ Ошибка при подготовке: {res.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Не удалось запустить скрипт экспорта: {e}[/red]")

def handle_import_web(args):
    project = _validate_project_name(args.project)
    port = args.port
    query = args.query
    filename = args.filename
    
    console.print(Panel(
        f"[cyan]🔄 Запуск импорта веб-страницы для проекта [bold]{project}[/bold]...[/cyan]\n"
        f"🔌 Порт Chrome: [yellow]{port}[/yellow]\n"
        f"🔍 Поисковый запрос: [yellow]{query}[/yellow]\n"
        f"📁 Выходной файл: [cyan]input/{filename}[/cyan]",
        title="Импорт из браузера"
    ))
    
    import subprocess
    import sys
    try:
        res = subprocess.run([
            sys.executable, "scripts/import_web.py",
            "--project", project,
            "--port", str(port),
            "--query", query,
            "--filename", filename
        ], capture_output=True, text=True)
        
        if res.returncode == 0:
            console.print(Panel(
                f"[green]✅ Импорт успешно завершен![/green]\n\n"
                f"{res.stdout.strip()}",
                title="Результат импорта",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]❌ Ошибка при импорте веб-страницы:[/red]\n\n"
                f"{res.stderr.strip()}",
                title="Ошибка импорта",
                border_style="red"
            ))
    except Exception as e:
        console.print(f"[red]❌ Не удалось запустить скрипт импорта: {e}[/red]")

def handle_update(args):
    """Скрипт для автоматического обновления Requirements Mind до актуальной версии с GitHub"""
    console.print("[bold cyan]🔄 Запущено автоматическое обновление Requirements Mind...[/bold cyan]")
    
    is_git = os.path.exists(".git")
    
    if is_git:
        console.print("  • Обнаружен репозиторий Git. Выполняется обновление из репозитория... ")
        try:
            import subprocess
            res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, check=True)
            console.print("[green]OK[/green]")
            console.print(f"[dim]{res.stdout.strip()}[/dim]")
        except Exception as e:
            console.print("[red]ОШИБКА[/red]")
            console.print(f"[red]Не удалось выполнить git pull: {e}[/red]")
            console.print("[yellow]Попытка обновить через прямую загрузку ZIP-архива...[/yellow]")
            is_git = False
            
    if not is_git:
        console.print("  • Загрузка свежего дистрибутива с GitHub... ")
        import urllib.request
        import zipfile
        import tempfile
        
        url = "https://github.com/Menta1ik/requirements-mind/archive/refs/heads/main.zip"
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                zip_data = response.read()
            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]ОШИБКА[/red]")
            console.print(f"[red]Не удалось скачать файлы обновления: {e}[/red]")
            return
            
        console.print("  • Распаковка и обновление файлов ядра... ")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "dist.zip")
                with open(zip_path, "wb") as f:
                    f.write(zip_data)
                    
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                extracted_items = os.listdir(temp_dir)
                dist_folder_name = None
                for item in extracted_items:
                    if item.startswith("requirements-mind") and os.path.isdir(os.path.join(temp_dir, item)):
                        dist_folder_name = item
                        break
                        
                if not dist_folder_name:
                    raise Exception("Не удалось найти папку дистрибутива в архиве.")
                    
                dist_folder_path = os.path.join(temp_dir, dist_folder_name)
                
                # Обновляем только файлы ядра
                items_to_update = ["cli.py", "requirements.txt", "install.py", "skills", "kb", "docs", "flows", "scripts"]
                for item in items_to_update:
                    src_item = os.path.join(dist_folder_path, item)
                    dest_item = os.path.join(os.getcwd(), item)
                    if os.path.exists(src_item):
                        if os.path.isdir(src_item):
                            if os.path.exists(dest_item):
                                shutil.rmtree(dest_item)
                            shutil.copytree(src_item, dest_item)
                        else:
                            shutil.copy2(src_item, dest_item)
            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]ОШИБКА[/red]")
            console.print(f"[red]Не удалось распаковать файлы обновления: {e}[/red]")
            return

    console.print("  • Проверка и обновление зависимостей Python... ")
    try:
        import subprocess
        venv_pip = os.path.join(".venv", "bin", "pip") if os.path.exists(os.path.join(".venv", "bin", "pip")) else "pip"
        if shutil.which("uv"):
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True)
        else:
            subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True, capture_output=True)
        console.print("[green]OK[/green]")
    except Exception as e:
        console.print(f"[yellow]Предупреждение: Не удалось обновить зависимости: {e}[/yellow]")

    console.print("  • Перенастройка ИИ-навыков в IDE... ")
    try:
        class DummyArgs:
            pass
        handle_setup_ide(DummyArgs())
        console.print("[green]OK[/green]")
    except Exception as e:
        console.print("[red]ОШИБКА[/red]")
        console.print(f"[red]Не удалось обновить навыки в IDE: {e}[/red]")
        return

    console.print(Panel(
        "[bold green]🎉 Requirements Mind успешно обновлен до последней версии с GitHub![/bold green]\n\n"
        "• Все файлы ядра, шаблоны и базы знаний обновлены.\n"
        "• Зависимости переустановлены.\n"
        "• ИИ-навыки и слэш-команды повторно скопированы во все IDE.\n\n"
        "[white]Снова запустите [bold]/reqmind[/bold] в чате IDE, чтобы увидеть новые возможности![/white]",
        title="Обновление успешно завершено"
    ))

def handle_setup_ide(args):
    """Скрипт для настройки локального окружения ИИ-ассистентов аналитика (копирует навыки в служебные папки IDE)"""
    console.print("[cyan]⚙️ Настройка локального окружения ИИ-ассистентов IDE для аналитика...[/cyan]")
    
    ide_mappings = {
        ".agent/skills": "Google Antigravity",
        ".claude/skills": "Claude Code",
        ".agents/skills": "Cursor / Copilot",
        ".codex/skills": "OpenAI Codex CLI"
    }
    
    src_rm = "skills/rm"
    src_bmad = "skills/bmad"
    
    if not os.path.exists(src_rm) or not os.path.exists(src_bmad):
        console.print("[red]❌ Ошибка: Папки с навыками skills/rm/ или skills/bmad/ отсутствуют в проекте. Сначала склонируйте репозиторий полностью.[/red]")
        return
        
    for dest_dir, ide_name in ide_mappings.items():
        os.makedirs(dest_dir, exist_ok=True)
        console.print(f"🔗 Конфигурация для [yellow]{ide_name}[/yellow] ({dest_dir})...")
        
        # Копируем навыки RM
        for file in os.listdir(src_rm):
            if file.endswith(".md"):
                shutil.copy2(os.path.join(src_rm, file), os.path.join(dest_dir, file))
                
        # Копируем навыки BMAD
        for folder in os.listdir(src_bmad):
            src_folder = os.path.join(src_bmad, folder)
            if os.path.isdir(src_folder):
                dest_folder = os.path.join(dest_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder)
                shutil.copytree(src_folder, dest_folder)
                
    # Синхронизируем локальные кастомизации в _bmad/custom/
    src_custom = "skills/custom"
    dest_custom = "_bmad/custom"
    if os.path.exists(src_custom):
        os.makedirs(dest_custom, exist_ok=True)
        console.print(f"⚙️ Синхронизация локальных кастомизаций агентов BMAD ({dest_custom})...")
        for file in os.listdir(src_custom):
            if file.endswith(".toml"):
                shutil.copy2(os.path.join(src_custom, file), os.path.join(dest_custom, file))
                
    console.print(Panel(
        "[green]🎉 Все ИИ-навыки успешно импортированы в локальные служебные каталоги вашей IDE![/green]\n\n"
        "[bold white]Теперь ваши ИИ-помощники (Claude Code, Cursor, Antigravity, OpenAI Codex) полностью готовы выполнять роли ИИ-агентов Requirements Mind![/bold white]",
        title="Настройка IDE завершена"
    ))

# =====================================================================
# Диагностика и ручное управление FSM (status / reset)
# =====================================================================

# Разрешённые целевые статусы для `cli.py reset`. Любой иной отвергается до
# того, как state.json будет переписан — это защищает FSM от опечаток.
_VALID_STATUSES = {
    "onboarding",
    "intake",
    "needs_questions",
    "drafting",
    "validating",
    "needs_revision",
    "approved",
}


def _list_artifacts(project_dir: str) -> Dict[str, List[str]]:
    """Возвращает краткую сводку артефактов проекта по поддиректориям."""
    out: Dict[str, List[str]] = {}
    for sub in ("input", "draft", "messages", "validation", "analysis", "final"):
        path = os.path.join(project_dir, sub)
        if os.path.isdir(path):
            out[sub] = sorted(f for f in os.listdir(path) if not f.startswith("."))
        else:
            out[sub] = []
    return out


def handle_status(args):
    """Показывает состояние FSM проекта, последние артефакты и открытые вопросы.

    Это «диагностическая» команда — она не меняет ни одного файла. Полезна,
    когда автоматика ИИ-агента не сработала и нужно понять, в каком статусе
    застрял проект и какие файлы реально лежат на диске.
    """
    project = _validate_project_name(args.project)
    project_dir = get_project_dir(project)
    if not os.path.isdir(project_dir):
        console.print(f"[red]❌ Проект [bold]{project}[/bold] не найден ({project_dir}).[/red]")
        sys.exit(1)

    state = load_state_safe(project)
    if state is None:
        console.print(
            f"[red]❌ Файл state.json повреждён или отсутствует в {project_dir}.[/red]\n"
            f"[white]Запустите [cyan]uv run cli.py init --project={project}[/cyan] для пересоздания "
            f"(существующие артефакты не пострадают), либо отредактируйте state.json вручную.[/white]"
        )
        sys.exit(1)

    artifacts = _list_artifacts(project_dir)
    context_path = os.path.join(project_dir, "context.md")
    fm = _read_frontmatter(context_path) if os.path.exists(context_path) else {}
    rm_status_marker = fm.get("rm_status", "—")

    def _fmt(items: List[str]) -> str:
        if not items:
            return "[dim]пусто[/dim]"
        head = ", ".join(items[:5])
        tail = "" if len(items) <= 5 else f" [dim]… (+{len(items) - 5})[/dim]"
        return f"{head}{tail}"

    console.print(Panel(
        f"📁 [bold]{project}[/bold]  ([cyan]{project_dir}[/cyan])\n"
        f"⚙️  Статус FSM:        [yellow]{state.status}[/yellow]\n"
        f"📄  Документ цикла:    [white]{state.document}[/white] (итерация v{state.iteration})\n"
        f"🎯  Профиль:           [white]{state.profile if state.profile is not None else '—'}[/white]\n"
        f"🤖  Активные агенты:   [white]{', '.join(state.active_agents) or '—'}[/white]\n"
        f"❓  Открытых вопросов: [white]{state.open_questions}[/white]\n"
        f"🕒  Обновлено:         [dim]{state.last_updated}[/dim]\n"
        f"🏷  context.md marker: [white]rm_status: {rm_status_marker}[/white]"
        f"{'  [yellow](frontmatter отсутствует)[/yellow]' if not fm else ''}\n\n"
        f"[bold]Артефакты:[/bold]\n"
        f"  • [cyan]input/[/cyan]      {_fmt(artifacts['input'])}\n"
        f"  • [cyan]draft/[/cyan]      {_fmt(artifacts['draft'])}\n"
        f"  • [cyan]messages/[/cyan]   {_fmt(artifacts['messages'])}\n"
        f"  • [cyan]validation/[/cyan] {_fmt(artifacts['validation'])}\n"
        f"  • [cyan]analysis/[/cyan]   {_fmt(artifacts['analysis'])}\n"
        f"  • [cyan]final/[/cyan]      {_fmt(artifacts['final'])}",
        title=f"Requirements Mind — статус проекта {project}",
        border_style="cyan",
    ))


def handle_reset(args):
    """Переводит FSM проекта в указанный статус — для ручного отката или починки.

    По умолчанию требует подтверждения (`--yes` для тихого режима). Никаких
    файлов артефактов не трогает: переписывает только state.json. Если нужно
    «снести проект и начать с нуля» — удаляйте папку projects/<name>/ руками.
    """
    project = _validate_project_name(args.project)
    target = args.to.strip().lower()
    if target not in _VALID_STATUSES:
        console.print(
            f"[red]❌ Недопустимый целевой статус: {target!r}.[/red]\n"
            f"[white]Разрешены: {', '.join(sorted(_VALID_STATUSES))}.[/white]"
        )
        sys.exit(2)

    state = load_state_safe(project)
    if state is None:
        console.print(f"[red]❌ state.json не найден для проекта {project}.[/red]")
        sys.exit(1)

    old_status = state.status
    if old_status == target:
        console.print(f"[yellow]ℹ️ Проект уже находится в статусе [bold]{target}[/bold] — ничего не меняю.[/yellow]")
        return

    if not args.yes:
        console.print(
            f"[yellow]⚠️ Текущий статус: [bold]{old_status}[/bold] → новый: [bold]{target}[/bold].[/yellow]\n"
            f"[white]Подтвердите переход в [cyan]projects/{project}/state.json[/cyan][/white]"
        )
        try:
            answer = input("Продолжить? [y/N]: ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            console.print("[red]❌ Отменено пользователем.[/red]")
            sys.exit(1)

    state.status = target
    # Сбрасываем active_agents к разумному дефолту для нового статуса.
    default_agents = {
        "onboarding": ["a0"],
        "intake": ["a1"],
        "needs_questions": ["a3"],
        "drafting": ["a4"],
        "validating": ["a2"],
        "needs_revision": ["a4"],
        "approved": ["master-orchestrator"],
    }
    state.active_agents = default_agents.get(target, state.active_agents)
    save_state(project, state)

    console.print(Panel(
        f"[green]✅ Статус успешно изменён.[/green]\n"
        f"[bold]{old_status}[/bold] → [bold yellow]{target}[/bold yellow]\n"
        f"Active agents: [white]{', '.join(state.active_agents)}[/white]\n\n"
        f"[white]Запустите [cyan]uv run cli.py status --project={project}[/cyan] для проверки.[/white]",
        title="reset FSM",
        border_style="green",
    ))


# =====================================================================
# Main Парсер Argparse
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Requirements Mind CLI — Инструмент управления требованиями нового поколения на базе BMAD METHOD."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Команды")

    # init
    parser_init = subparsers.add_parser("init", help="Инициализировать новый проект")
    parser_init.add_argument("--project", required=True, help="Название нового проекта")
    parser_init.set_defaults(func=handle_init)

    # onboard
    parser_onboard = subparsers.add_parser("onboard", help="Зафиксировать завершение онбординга и перейти к Intake")
    parser_onboard.add_argument("--project", required=True, help="Название проекта")
    parser_onboard.set_defaults(func=handle_onboard)

    # intake
    parser_intake = subparsers.add_parser("intake", help="Зафиксировать разбор входов и проверить context.md")
    parser_intake.add_argument("--project", required=True, help="Название проекта")
    parser_intake.set_defaults(func=handle_intake)

    # draft
    parser_draft = subparsers.add_parser("draft", help="Зафиксировать создание черновика")
    parser_draft.add_argument("--project", required=True, help="Название проекта")
    parser_draft.add_argument("--doc", default="BRD", help="Тип документа (BRD/SRS/Tech-Design/API-Contract)")
    parser_draft.set_defaults(func=handle_draft)

    # validate
    parser_validate = subparsers.add_parser("validate", help="Считать отчет валидации и перевести проект далее")
    parser_validate.add_argument("--project", required=True, help="Название проекта")
    parser_validate.add_argument("--doc", default="BRD", help="Тип документа")
    parser_validate.add_argument("--version", type=int, default=1, help="Версия черновика")
    parser_validate.set_defaults(func=handle_validate)

    # final
    parser_final = subparsers.add_parser("final", help="Финализировать одобренный черновик")
    parser_final.add_argument("--project", required=True, help="Название проекта")
    parser_final.add_argument("--doc", default="BRD", help="Тип документа")
    parser_final.add_argument("--version", type=int, required=True, help="Версия черновика")
    parser_final.set_defaults(func=handle_final)

    # analyze
    parser_analyze = subparsers.add_parser("analyze", help="Зафиксировать аналитическую задачу Режима B")
    parser_analyze.add_argument("--project", required=True, help="Название проекта")
    parser_analyze.add_argument("--task", required=True, help="Суть аналитического исследования")
    parser_analyze.set_defaults(func=handle_analyze)

    # Augment: доработка существующего документа артефактами (защищённый режим, см. flows/09-augment.md)
    parser_augment = subparsers.add_parser(
        "augment",
        help="Запустить augment-режим: дополнить существующий документ артефактами, сохранив структуру"
    )
    parser_augment.add_argument("--project", required=True, help="Название проекта")
    parser_augment.add_argument("--baseline", required=True, help="Путь к baseline-документу (SRS/BRD/Tech-Design/API-Contract)")
    parser_augment.add_argument("--doc", required=True, help="Тип документа: BRD / SRS / Tech-Design / API-Contract")
    parser_augment.set_defaults(func=handle_augment)

    # collaborate
    parser_collaborate = subparsers.add_parser("collaborate", help="Подсказать инструкцию для Party Mode")
    parser_collaborate.add_argument("--project", required=True, help="Название проекта")
    parser_collaborate.add_argument("--agents", default="a2,a4", help="Список кодов агентов через запятую")
    parser_collaborate.set_defaults(func=handle_collaborate)

    # sync-vault
    parser_sync = subparsers.add_parser("sync-vault", help="Синхронизировать папки проектов с Obsidian Vault")
    parser_sync.set_defaults(func=handle_sync_vault)

    # export-notebooklm
    parser_export = subparsers.add_parser("export-notebooklm", help="Экспортировать проект для NotebookLM")
    parser_export.add_argument("--project", required=True, help="Название проекта")
    parser_export.set_defaults(func=handle_export_notebooklm)

    # import-web
    parser_import = subparsers.add_parser("import-web", help="Автономно импортировать страницу из Chrome (CDP) в input/")
    parser_import.add_argument("--project", required=True, help="Название проекта")
    parser_import.add_argument("--port", type=int, default=9222, help="Порт отладки Chrome (по умолчанию 9222)")
    parser_import.add_argument("--query", required=True, help="Поисковый запрос для поиска вкладки (по URL или заголовку)")
    parser_import.add_argument("--filename", default="confluence_specs.md", help="Имя выходного файла в папке input/")
    parser_import.set_defaults(func=handle_import_web)

    # setup-ide
    parser_setup = subparsers.add_parser("setup-ide", help="Настроить локальные папки ИИ-ассистентов IDE для нового аналитика")
    parser_setup.set_defaults(func=handle_setup_ide)

    # update
    parser_update = subparsers.add_parser("update", help="Обновить Requirements Mind до последней версии с GitHub")
    parser_update.set_defaults(func=handle_update)

    # status (диагностика)
    parser_status = subparsers.add_parser("status", help="Показать текущий статус FSM и артефакты проекта")
    parser_status.add_argument("--project", required=True, help="Название проекта")
    parser_status.set_defaults(func=handle_status)

    # reset (ручное управление FSM)
    parser_reset = subparsers.add_parser("reset", help="Принудительно перевести FSM в указанный статус")
    parser_reset.add_argument("--project", required=True, help="Название проекта")
    parser_reset.add_argument(
        "--to",
        required=True,
        help="Целевой статус: onboarding|intake|needs_questions|drafting|validating|needs_revision|approved",
    )
    parser_reset.add_argument("--yes", action="store_true", help="Не запрашивать подтверждение")
    parser_reset.set_defaults(func=handle_reset)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)

if __name__ == "__main__":
    main()
