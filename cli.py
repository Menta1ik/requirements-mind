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
# Helpers: project name validation and frontmatter parsing
# =====================================================================

_PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _validate_project_name(name: str) -> str:
    """Checks that the project name is safe to use in filesystem paths.

    Allows only Latin letters, digits, hyphen and underscore; length 1-64.
    This blocks path traversal attempts via --project=../../etc and the like.
    """
    if not _PROJECT_NAME_RE.match(name or ""):
        console.print(
            f"[red]❌ Invalid project name: {name!r}.[/red]\n"
            f"[white]Allowed characters [bold][A-Za-z0-9_-][/bold], length 1-64.[/white]"
        )
        sys.exit(2)
    return name


def _read_frontmatter(path: str) -> Dict[str, Any]:
    """Reads YAML-like frontmatter from the start of a Markdown file.

    Supports a minimal format:
        ---
        key1: value1
        key2: value2
        ---
    Returns a dict of string pairs (values lower-cased and trimmed).
    If frontmatter is missing or the file is unreadable, returns an empty dict.
    Intentionally without a PyYAML dependency: frontmatter in Requirements Mind
    contains flat `key: value` pairs and does not require full YAML.
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
    profile: Optional[int] = None  # 1-6 matching the target requirement project profiles
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
    
    # Create template files in input if the folder is empty
    input_dir = os.path.join(base_dir, "input")
    if not os.listdir(input_dir):
        with open(os.path.join(input_dir, "transcript.md"), "w", encoding="utf-8") as f:
            f.write("# Meeting transcript\n\n*(Paste the project discussion transcript here)*\n")
        with open(os.path.join(input_dir, "requirements.md"), "w", encoding="utf-8") as f:
            f.write("# Initial requirements\n\n*(Paste raw requirements or tickets here)*\n")

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
# CLI Command Logic
# =====================================================================

def handle_init(args):
    project = _validate_project_name(args.project)
    ensure_project_dirs(project)
    state = load_state(project)
    
    console.print(Panel.fit(
        f"[bold green]Successfully initialized project: {project}[/bold green]\n"
        f"📁 Path: [cyan]{get_project_dir(project)}[/cyan]\n"
        f"⚙️ Current status: [yellow]{state.status}[/yellow]\n\n"
        f"[bold white]Next step:[/bold white]\n"
        f"1. Ask the AI assistant in your IDE (Cursor, Claude Code, Antigravity, Codex) to start onboarding:\n"
        f"   [yellow]\"Mary, let's start onboarding (RMONB) for the new project {project}\"[/yellow]\n"
        f"2. After the onboarding interview and preparing the raw files in input/, record it in the CLI:\n"
        f"   [yellow]uv run cli.py onboard --project={project}[/yellow]",
        title="[bold]Requirements Mind — Initialization[/bold]"
    ))

def handle_onboard(args):
    project = _validate_project_name(args.project)
    state = load_state(project)
    if state.status != "onboarding":
        console.print(f"[yellow]⚠️ Project {project} has already passed the onboarding stage (current status: {state.status}).[/yellow]")
        return

    state.status = "intake"
    state.active_agents = ["a1"]
    save_state(project, state)

    console.print(Panel(
        f"[green]🎉 Onboarding of project [bold]{project}[/bold] completed successfully![/green]\n\n"
        f"Project status changed to: [yellow]intake[/yellow] (ready for requirements analysis).\n\n"
        f"[bold white]WHAT TO DO NEXT:[/bold white]\n"
        f"1. Make sure the raw requirement files are in [cyan]projects/{project}/input/[/cyan]\n"
        f"2. Ask the AI assistant in your IDE to run the Intake analysis:\n"
        f"   [yellow]\"Run the a1-intake-analyst skill for project {project} and create context.md\"[/yellow]\n"
        f"3. After the analysis is done, record the status in the terminal:\n"
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
            f"[red]❌ Error: File [bold]context.md[/bold] not found at {context_path}[/red]\n\n"
            f"[bold white]How to fix:[/bold white]\n"
            f"Ask your AI assistant in the IDE (for example, Cursor or Claude Code) to run the [cyan]a1-intake-analyst[/cyan] skill from the [cyan]skills/rm/[/cyan] folder to analyze the files in [cyan]input/[/cyan] and write [cyan]context.md[/cyan].\n"
            f"Once the AI generates the file, run this command again.",
            title="Error: Missing context.md"
        ))
        return

    # Control signal — the explicit frontmatter `rm_status: complete|incomplete`.
    # The free-text substring match is kept only as a fallback for backward
    # compatibility (contexts written before v2.1). Since agents are now
    # language-agnostic, the fallback matches both the legacy Russian markers
    # and their English equivalents.
    fm = _read_frontmatter(context_path)
    if "rm_status" in fm:
        has_gaps = fm["rm_status"] != "complete"
    else:
        with open(context_path, "r", encoding="utf-8") as f:
            context_content = f.read()
        lowered = context_content.lower()
        has_gaps = (
            "Флаг неполноты" in context_content
            or "недостаточно" in lowered
            or "Incompleteness flag" in context_content
            or "insufficient" in lowered
        )
        console.print(
            "[yellow]⚠️ context.md has no `rm_status` frontmatter. "
            "Falling back to the legacy substring matcher. "
            "Ask the A1 AI agent to add `rm_status: complete|incomplete` frontmatter at the top of the file.[/yellow]"
        )
    
    if has_gaps:
        state.status = "needs_questions"
        state.active_agents = ["a3"]
        save_state(project, state)
        console.print(Panel(
            f"[yellow]⚠️ An incompleteness flag for the requirements was detected in context.md![/yellow]\n\n"
            f"[bold white]Next step:[/bold white]\n"
            f"1. Ask your AI assistant in the IDE to run the [cyan]a3-question-generator[/cyan] skill to generate clarifying questions in [cyan]questions.md[/cyan].\n"
            f"2. Answer the questions and save them in [cyan]qa-history.md[/cyan].\n"
            f"3. Ask the AI again to update [cyan]context.md[/cyan], removing the incompleteness flag, and rerun: [yellow]uv run cli.py intake --project={project}[/yellow]",
            title="Requirements incomplete"
        ))
    else:
        state.status = "drafting"
        state.active_agents = ["a4"]
        save_state(project, state)
        console.print(Panel(
            f"[green]✅ context.md was successfully checked and recorded![/green]\n"
            f"⚙️ New project status: [yellow]{state.status}[/yellow] (ready for drafting)\n\n"
            f"[bold white]Next step:[/bold white]\n"
            f"Ask the AI assistant in the IDE to run the [cyan]a4-document-writer[/cyan] skill to generate the first draft [cyan]draft/{state.document}-v{state.iteration}.md[/cyan] following the knowledge base checklists.\n"
            f"After generating it, run the command: [yellow]uv run cli.py draft --project={project} --doc={state.document}[/yellow]",
            title="Context ready"
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
            f"[red]❌ Error: Draft file [bold]{draft_file}[/bold] not found at {draft_path}[/red]\n\n"
            f"[bold white]How to fix:[/bold white]\n"
            f"Ask your AI assistant in the IDE to run the [cyan]a4-document-writer[/cyan] skill to write the [cyan]{doc}[/cyan] document and save it at [cyan]draft/{draft_file}[/cyan].\n"
            f"After generating the file, run this command again.",
            title="Draft not found"
        ))
        return

    state.status = "validating"
    state.active_agents = ["a2"]
    state.document = doc
    save_state(project, state)
    
    console.print(Panel(
        f"[green]✅ Draft {draft_file} was successfully detected and recorded![/green]\n"
        f"⚙️ New project status: [yellow]{state.status}[/yellow] (ready for validation)\n\n"
        f"[bold white]Next step:[/bold white]\n"
        f"Ask the AI assistant in the IDE to run the [cyan]a2-requirements-validator[/cyan] skill to check the draft quality and save the report in [cyan]messages/a2-to-a4-v{state.iteration}.md[/cyan].\n"
        f"After validation passes, run: [yellow]uv run cli.py validate --project={project} --doc={doc} --version={state.iteration}[/yellow]",
        title="Draft recorded"
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
            f"[red]❌ Error: Validation report [bold]{report_file}[/bold] not found in the messages/ folder[/red]\n\n"
            f"[bold white]How to fix:[/bold white]\n"
            f"Ask your AI assistant in the IDE to run the [cyan]a2-requirements-validator[/cyan] skill to check the draft [cyan]{doc}-v{version}.md[/cyan].\n"
            f"The AI should analyze the draft against the checklists and write the report to [cyan]messages/{report_file}[/cyan].\n"
            f"After that, run the validate command again.",
            title="Report not found"
        ))
        return

    # Control signal — the explicit frontmatter `rm_verdict: passed|failed`.
    # Fallback — the narrow marker `**Verdict:** FAILED` (not a bare "FAILED",
    # which would trigger on harmless phrases like "FAILED is not acceptable").
    # Both the legacy Russian marker and the English one are accepted.
    fm = _read_frontmatter(report_path)
    if "rm_verdict" in fm:
        is_failed = fm["rm_verdict"] != "passed"
    else:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        is_failed = "**Вердикт:** FAILED" in report_content or "**Verdict:** FAILED" in report_content
        console.print(
            "[yellow]⚠️ The report has no `rm_verdict` frontmatter. "
            "Falling back to the legacy `**Verdict:** FAILED` marker. "
            "Ask the A2 AI agent to add `rm_verdict: PASSED|FAILED` frontmatter at the top of the report.[/yellow]"
        )
    
    if is_failed:
        state.status = "needs_revision"
        state.active_agents = ["a4"]
        save_state(project, state)
        console.print(Panel(
            f"[bold red]❌ Validation did not pass (FAILED) for version v{version}![/bold red]\n"
            f"The report is saved in [cyan]messages/{report_file}[/cyan]\n\n"
            f"[bold white]Next step:[/bold white]\n"
            f"1. Ask the AI assistant in the IDE to run the [cyan]a4-document-writer[/cyan] skill to fix the document based on the report's findings.\n"
            f"2. The AI should save the corrected document as [cyan]draft/{doc}-v{version}.md[/cyan] (or increment the version).\n"
            f"3. After the fix, rerun the validate command.",
            title="Validation FAILED"
        ))
    else:
        state.status = "approved"
        state.active_agents = ["master-orchestrator"]
        save_state(project, state)
        console.print(Panel(
            f"[bold green]✅ Validation passed successfully (PASSED) for version v{version}![/bold green]\n\n"
            f"[bold white]Next step:[/bold white]\n"
            f"Run the document approval and finalization command:\n"
            f"[yellow]uv run cli.py final --project={project} --doc={doc} --version={version}[/yellow]",
            title="Validation PASSED"
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
        console.print(f"[red]❌ Error: Draft {draft_file} not found.[/red]")
        return

    final_file = f"{doc}-v{version}-final.md"
    final_path = os.path.join(project_dir, "final", final_file)

    try:
        shutil.copy2(draft_path, final_path)
    except Exception as e:
        console.print(f"[red]❌ Error copying the file to final: {e}[/red]")
        return

    # Create the orchestrator log
    decision_path = os.path.join(project_dir, "messages", "orchestrator-decision.md")
    decision_text = (
        f"# Orchestrator finalization decision\n\n"
        f"* **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"* **Project:** {project}\n"
        f"* **Document:** {doc}\n"
        f"* **Approved version:** v{version}\n\n"
        f"The document successfully passed validation and was moved to the final specifications folder: `final/{final_file}`.\n"
    )
    with open(decision_path, "w", encoding="utf-8") as f:
        f.write(decision_text)

    # Advance the hierarchy chain forward: BRD -> SRS -> Tech-Design -> API-Contract
    hierarchy = ["BRD", "SRS", "Tech-Design", "API-Contract"]
    try:
        curr_idx = hierarchy.index(doc)
        if curr_idx < len(hierarchy) - 1:
            next_doc = hierarchy[curr_idx + 1]
            state.document = next_doc
            state.status = "intake"
            state.active_agents = ["a1"]
            state.iteration = 1
            next_step_msg = f"The chain has advanced to the next document: [bold yellow]{next_doc}[/bold yellow]."
        else:
            state.status = "approved"
            state.active_agents = []
            next_step_msg = "🎉 Congratulations! The full specification chain BRD → SRS → Tech Design → API Contract has been successfully developed!"
    except ValueError:
        state.status = "approved"
        next_step_msg = "The specification was successfully completed."

    save_state(project, state)

    console.print(Panel(
        f"[green]🎉 Successfully finalized the specification: {doc}[/green]\n"
        f"📁 File saved: [cyan]final/{final_file}[/cyan]\n"
        f"⚖️ Decision recorded in [cyan]messages/orchestrator-decision.md[/cyan]\n\n"
        f"[bold white]Next project status:[/bold white] {state.status}\n"
        f"{next_step_msg}",
        title="Finalization complete"
    ))

def handle_augment(args):
    """Starts augment mode: baseline document + artifacts → augmented version.

    The command:
      1) copies the baseline to projects/<name>/input/baseline/<filename>,
      2) writes/updates context.md with frontmatter rm_mode: augment + baseline_doc.*,
      3) sets state.json to status=drafting, mode=augment, document=<doc>,
      4) prints an instruction for the AI assistant to run A1 → A4 in protected mode.

    The augment mode contract is described in:
      - flows/09-augment.md
      - skills/rm/a4-document-writer.md (the "Augment Mode" block)
      - skills/rm/a1-intake-analyst.md (distinguishing baseline vs artifacts)
      - skills/rm/master-orchestrator.md (enforcing the contract)
    """
    project = _validate_project_name(args.project)
    baseline_arg = args.baseline
    doc = args.doc

    # 1. Input checks
    allowed_docs = {"BRD", "SRS", "Tech-Design", "API-Contract"}
    if doc not in allowed_docs:
        console.print(
            f"[red]❌ Invalid document type: {doc!r}.[/red]\n"
            f"Allowed: {', '.join(sorted(allowed_docs))}."
        )
        sys.exit(2)

    if not os.path.isfile(baseline_arg):
        console.print(f"[red]❌ Baseline file not found: {baseline_arg}[/red]")
        sys.exit(2)

    # 2. Prepare folders and copy the baseline
    ensure_project_dirs(project)
    project_dir = get_project_dir(project)
    baseline_dir = os.path.join(project_dir, "input", "baseline")
    os.makedirs(baseline_dir, exist_ok=True)

    baseline_filename = os.path.basename(baseline_arg)
    baseline_dest = os.path.join(baseline_dir, baseline_filename)
    baseline_rel = os.path.join("input", "baseline", baseline_filename)

    # Do not copy onto itself if the user already placed the file in input/baseline/
    if os.path.abspath(baseline_arg) != os.path.abspath(baseline_dest):
        shutil.copy2(baseline_arg, baseline_dest)

    # 3. Update/create context.md with the augment frontmatter
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
        # Preserve the existing content, replace only the frontmatter
        with open(context_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing.startswith("---"):
            # Strip the old frontmatter
            end = existing.find("\n---", 3)
            if end != -1:
                body = existing[end + 4 :].lstrip("\n")
            else:
                body = existing  # malformed frontmatter, leave it alone
        else:
            body = existing
        new_context = augment_frontmatter + "\n" + body
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(new_context)
        context_action = "updated"
    else:
        starter_body = (
            "# 🎯 Vision and business goals\n\n*(A1 will fill this in from the artifacts)*\n\n"
            "# 👥 Stakeholders\n\n*(A1 will fill this in from the artifacts)*\n\n"
            "# ⚡ Constraints\n\n*(A1 will fill this in from the artifacts)*\n\n"
            "## 🔄 Delta for augmenting the baseline\n\n"
            f"*(A1 will describe here: what is new from the artifacts and where to integrate it in `{baseline_rel}`)*\n\n"
            "## ❓ Open questions and gaps\n\n"
            "*(A1 / A3 maintain the registry here)*\n"
        )
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(augment_frontmatter + "\n" + starter_body)
        context_action = "created"

    # 4. Update state.json
    state = load_state(project)
    state.mode = "augment"
    state.document = doc
    state.status = "drafting"
    state.active_agents = ["a1"]  # A1 parses the artifacts under augment first
    save_state(project, state)

    # 5. Instruction for the user
    console.print(Panel(
        f"[green]🛡️  Augment mode activated for project [bold]{project}[/bold][/green]\n\n"
        f"📄 Baseline: [cyan]{baseline_rel}[/cyan]  (type: {doc})\n"
        f"📝 context.md {context_action} with frontmatter [yellow]rm_mode: augment[/yellow]\n"
        f"⚙️  state.json: status=[yellow]drafting[/yellow], mode=[yellow]augment[/yellow]\n\n"
        f"[bold white]What to do next:[/bold white]\n"
        f"1. Place the remaining artifacts (transcripts, notes, new BRs) in [cyan]projects/{project}/input/[/cyan] "
        f"(NOT in the baseline/ subfolder).\n"
        f"2. Ask the AI assistant in the IDE:\n"
        f"   [yellow]\"Run a1-intake-analyst for project {project}. "
        f"This is augment mode, the baseline is {baseline_rel}, do not dissolve it into context.md, "
        f"describe only the delta from the artifacts\"[/yellow]\n"
        f"3. Once A1 has written context.md and context-changelog.md, record it:\n"
        f"   [cyan]uv run cli.py intake --project={project}[/cyan]\n"
        f"4. Then ask the AI to run [cyan]a4-document-writer[/cyan]. "
        f"It must show a diff plan in the chat and wait for your OK before writing "
        f"[cyan]draft/{doc}-v<N>.md[/cyan].\n\n"
        f"[dim]The baseline protection contract is described in flows/09-augment.md.[/dim]",
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
        f"[cyan]📈 Analytical task recorded: \"{task}\"[/cyan]\n\n"
        f"[bold white]How to run the analysis:[/bold white]\n"
        f"1. Open a conversation with your AI assistant in the IDE.\n"
        f"2. Ask the AI to run the [cyan]a6-analysis-writer[/cyan] skill to perform the task: [yellow]\"{task}\"[/yellow].\n"
        f"3. The AI will analyze the project context and write the report to [cyan]analysis/analysis-vN.md[/cyan].",
        title="Mode B — Analytical session"
    ))

def handle_collaborate(args):
    project = _validate_project_name(args.project)
    agents = args.agents
    state = load_state(project)
    agents_list = [a.strip() for a in agents.split(",")]

    console.print(Panel(
        f"[bold yellow]👥 Setting up a multi-agent round table (Party Mode) for project: {project}[/bold yellow]\n\n"
        f"[bold white]Instruction to start the discussion:[/bold white]\n"
        f"1. Open a chat with your AI assistant in the IDE.\n"
        f"2. Ask the AI to run the [cyan]bmad-party-mode[/cyan] skill (from the [cyan]skills/bmad/[/cyan] folder) with the following instruction:\n"
        f"   [green]\"Run a round table between agents {', '.join(agents_list)} to discuss the following problem: ...\"[/green]\n"
        f"3. The AI assistant will act as the orchestrator, invoke independent agents, and write the inter-agent communication log to [cyan]messages/collaborate-*.md[/cyan] files.",
        title="Start Party Mode"
    ))

def handle_sync_vault(args):
    console.print("[cyan]🔄 Running the Obsidian Vault synchronization script...[/cyan]")
    import subprocess
    try:
        # sys.executable instead of "python3" — on Windows the interpreter is usually "python",
        # while sys.executable points to the active venv on any OS.
        res = subprocess.run([sys.executable, "scripts/sync_to_vault.py"], capture_output=True, text=True)
        if res.returncode == 0:
            console.print("[green]✅ Obsidian synchronization completed successfully.[/green]")
        else:
            console.print(f"[red]❌ Error during synchronization: {res.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to run the synchronization script: {e}[/red]")

def handle_export_notebooklm(args):
    project = _validate_project_name(args.project)
    console.print(f"[cyan]📤 Preparing the NotebookLM export for project {project}...[/cyan]")
    import subprocess
    try:
        # sys.executable instead of "python3" — on Windows the interpreter is usually "python".
        res = subprocess.run([sys.executable, "scripts/export_to_notebooklm.py", "--project", project], capture_output=True, text=True)
        if res.returncode == 0:
            console.print("[green]✅ NotebookLM export prepared.[/green]")
        else:
            console.print(f"[red]❌ Error during preparation: {res.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to run the export script: {e}[/red]")

def handle_trace(args):
    """Runs the Tier 1 deterministic ID traceability linter (scripts/trace.py)."""
    project = _validate_project_name(args.project) if args.project else None
    import subprocess

    cmd = [sys.executable, "scripts/trace.py"]
    if project:
        cmd += ["--project", project]
    if args.doc:
        cmd += ["--doc", args.doc]
    if args.version:
        cmd += ["--version", str(args.version)]
    if args.file:
        cmd += ["--file", args.file]

    target = project or args.file or "?"
    console.print(Panel(
        f"[cyan]🔎 RM Trace Linter — ID and traceability check[/cyan]\n"
        f"📁 Target: [yellow]{target}[/yellow]"
        + (f"\n📄 Document: [yellow]{args.doc}[/yellow]" if args.doc else "")
        + (f"\n🔢 Version: [yellow]v{args.version}[/yellow]" if args.version else ""),
        title="Tier 1 validation",
    ))

    try:
        # stdout/stderr straight to the console — the linter formats its own output.
        res = subprocess.run(cmd)
        if res.returncode == 0:
            console.print("[green]✅ trace: no errors found.[/green]")
        elif res.returncode == 1:
            console.print("[red]❌ trace: traceability errors found (see the report above).[/red]")
        else:
            console.print(f"[red]❌ trace: launch error (code {res.returncode}).[/red]")
        sys.exit(res.returncode)
    except FileNotFoundError:
        console.print("[red]❌ scripts/trace.py not found — please reinstall Requirements Mind.[/red]")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]❌ Failed to run trace: {e}[/red]")
        sys.exit(2)


def handle_import_web(args):
    project = _validate_project_name(args.project)
    port = args.port
    query = args.query
    filename = args.filename
    
    console.print(Panel(
        f"[cyan]🔄 Importing a web page for project [bold]{project}[/bold]...[/cyan]\n"
        f"🔌 Chrome port: [yellow]{port}[/yellow]\n"
        f"🔍 Search query: [yellow]{query}[/yellow]\n"
        f"📁 Output file: [cyan]input/{filename}[/cyan]",
        title="Import from browser"
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
                f"[green]✅ Import completed successfully![/green]\n\n"
                f"{res.stdout.strip()}",
                title="Import result",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]❌ Error while importing the web page:[/red]\n\n"
                f"{res.stderr.strip()}",
                title="Import error",
                border_style="red"
            ))
    except Exception as e:
        console.print(f"[red]❌ Failed to run the import script: {e}[/red]")

def handle_update(args):
    """Script for automatically updating Requirements Mind to the current version from GitHub"""
    console.print("[bold cyan]🔄 Automatic update of Requirements Mind started...[/bold cyan]")

    is_git = os.path.exists(".git")

    if is_git:
        console.print("  • Git repository detected. Updating from the repository... ")
        try:
            import subprocess
            res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, check=True)
            console.print("[green]OK[/green]")
            console.print(f"[dim]{res.stdout.strip()}[/dim]")
        except Exception as e:
            console.print("[red]ERROR[/red]")
            console.print(f"[red]Failed to run git pull: {e}[/red]")
            console.print("[yellow]Attempting to update via direct ZIP archive download...[/yellow]")
            is_git = False

    if not is_git:
        console.print("  • Downloading a fresh distribution from GitHub... ")
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
            console.print("[red]ERROR[/red]")
            console.print(f"[red]Failed to download the update files: {e}[/red]")
            return

        console.print("  • Unpacking and updating the core files... ")
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
                    raise Exception("Could not find the distribution folder in the archive.")

                dist_folder_path = os.path.join(temp_dir, dist_folder_name)

                # Update only the core files
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
            console.print("[red]ERROR[/red]")
            console.print(f"[red]Failed to unpack the update files: {e}[/red]")
            return

    console.print("  • Checking and updating Python dependencies... ")
    try:
        import subprocess
        venv_pip = os.path.join(".venv", "bin", "pip") if os.path.exists(os.path.join(".venv", "bin", "pip")) else "pip"
        if shutil.which("uv"):
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True)
        else:
            subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True, capture_output=True)
        console.print("[green]OK[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to update dependencies: {e}[/yellow]")

    console.print("  • Reconfiguring AI skills in the IDE... ")
    try:
        class DummyArgs:
            pass
        handle_setup_ide(DummyArgs())
        console.print("[green]OK[/green]")
    except Exception as e:
        console.print("[red]ERROR[/red]")
        console.print(f"[red]Failed to update the IDE skills: {e}[/red]")
        return

    console.print(Panel(
        "[bold green]🎉 Requirements Mind was successfully updated to the latest version from GitHub![/bold green]\n\n"
        "• All core files, templates, and knowledge bases have been updated.\n"
        "• Dependencies have been reinstalled.\n"
        "• AI skills and slash commands have been re-copied into all IDEs.\n\n"
        "[white]Run [bold]/reqmind[/bold] again in the IDE chat to see the new features![/white]",
        title="Update completed successfully"
    ))

def handle_setup_ide(args):
    """Script for configuring the analyst's local AI assistant environment (copies skills into the IDE service folders)"""
    console.print("[cyan]⚙️ Configuring the local IDE AI assistant environment for the analyst...[/cyan]")
    
    ide_mappings = {
        ".agent/skills": "Google Antigravity",
        ".claude/skills": "Claude Code",
        ".agents/skills": "Cursor / Copilot",
        ".codex/skills": "OpenAI Codex CLI"
    }
    
    src_rm = "skills/rm"
    src_bmad = "skills/bmad"
    
    if not os.path.exists(src_rm) or not os.path.exists(src_bmad):
        console.print("[red]❌ Error: The skill folders skills/rm/ or skills/bmad/ are missing in the project. Clone the repository fully first.[/red]")
        return

    for dest_dir, ide_name in ide_mappings.items():
        os.makedirs(dest_dir, exist_ok=True)
        console.print(f"🔗 Configuration for [yellow]{ide_name}[/yellow] ({dest_dir})...")

        # Copy the RM skills
        for file in os.listdir(src_rm):
            if file.endswith(".md"):
                shutil.copy2(os.path.join(src_rm, file), os.path.join(dest_dir, file))

        # Copy the BMAD skills
        for folder in os.listdir(src_bmad):
            src_folder = os.path.join(src_bmad, folder)
            if os.path.isdir(src_folder):
                dest_folder = os.path.join(dest_dir, folder)
                if os.path.exists(dest_folder):
                    shutil.rmtree(dest_folder)
                shutil.copytree(src_folder, dest_folder)
                
    # Sync local customizations into _bmad/custom/
    src_custom = "skills/custom"
    dest_custom = "_bmad/custom"
    if os.path.exists(src_custom):
        os.makedirs(dest_custom, exist_ok=True)
        console.print(f"⚙️ Syncing local BMAD agent customizations ({dest_custom})...")
        for file in os.listdir(src_custom):
            if file.endswith(".toml"):
                shutil.copy2(os.path.join(src_custom, file), os.path.join(dest_custom, file))

    console.print(Panel(
        "[green]🎉 All AI skills were successfully imported into your IDE's local service directories![/green]\n\n"
        "[bold white]Your AI assistants (Claude Code, Cursor, Antigravity, OpenAI Codex) are now fully ready to act as Requirements Mind AI agents![/bold white]",
        title="IDE setup complete"
    ))

# =====================================================================
# FSM diagnostics and manual control (status / reset)
# =====================================================================

# Allowed target statuses for `cli.py reset`. Any other is rejected before
# state.json is rewritten — this protects the FSM from typos.
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
    """Returns a brief summary of the project artifacts by subdirectory."""
    out: Dict[str, List[str]] = {}
    for sub in ("input", "draft", "messages", "validation", "analysis", "final"):
        path = os.path.join(project_dir, sub)
        if os.path.isdir(path):
            out[sub] = sorted(f for f in os.listdir(path) if not f.startswith("."))
        else:
            out[sub] = []
    return out


def handle_status(args):
    """Shows the project's FSM state, latest artifacts, and open questions.

    This is a "diagnostic" command — it does not modify any file. Useful when
    the AI agent's automation did not fire and you need to understand which
    status the project is stuck in and which files actually exist on disk.
    """
    project = _validate_project_name(args.project)
    project_dir = get_project_dir(project)
    if not os.path.isdir(project_dir):
        console.print(f"[red]❌ Project [bold]{project}[/bold] not found ({project_dir}).[/red]")
        sys.exit(1)

    state = load_state_safe(project)
    if state is None:
        console.print(
            f"[red]❌ The state.json file is corrupted or missing in {project_dir}.[/red]\n"
            f"[white]Run [cyan]uv run cli.py init --project={project}[/cyan] to recreate it "
            f"(existing artifacts are not affected), or edit state.json manually.[/white]"
        )
        sys.exit(1)

    artifacts = _list_artifacts(project_dir)
    context_path = os.path.join(project_dir, "context.md")
    fm = _read_frontmatter(context_path) if os.path.exists(context_path) else {}
    rm_status_marker = fm.get("rm_status", "—")

    def _fmt(items: List[str]) -> str:
        if not items:
            return "[dim]empty[/dim]"
        head = ", ".join(items[:5])
        tail = "" if len(items) <= 5 else f" [dim]… (+{len(items) - 5})[/dim]"
        return f"{head}{tail}"

    console.print(Panel(
        f"📁 [bold]{project}[/bold]  ([cyan]{project_dir}[/cyan])\n"
        f"⚙️  FSM status:        [yellow]{state.status}[/yellow]\n"
        f"📄  Cycle document:    [white]{state.document}[/white] (iteration v{state.iteration})\n"
        f"🎯  Profile:           [white]{state.profile if state.profile is not None else '—'}[/white]\n"
        f"🤖  Active agents:     [white]{', '.join(state.active_agents) or '—'}[/white]\n"
        f"❓  Open questions:    [white]{state.open_questions}[/white]\n"
        f"🕒  Updated:           [dim]{state.last_updated}[/dim]\n"
        f"🏷  context.md marker: [white]rm_status: {rm_status_marker}[/white]"
        f"{'  [yellow](frontmatter missing)[/yellow]' if not fm else ''}\n\n"
        f"[bold]Artifacts:[/bold]\n"
        f"  • [cyan]input/[/cyan]      {_fmt(artifacts['input'])}\n"
        f"  • [cyan]draft/[/cyan]      {_fmt(artifacts['draft'])}\n"
        f"  • [cyan]messages/[/cyan]   {_fmt(artifacts['messages'])}\n"
        f"  • [cyan]validation/[/cyan] {_fmt(artifacts['validation'])}\n"
        f"  • [cyan]analysis/[/cyan]   {_fmt(artifacts['analysis'])}\n"
        f"  • [cyan]final/[/cyan]      {_fmt(artifacts['final'])}",
        title=f"Requirements Mind — project status: {project}",
        border_style="cyan",
    ))


def handle_reset(args):
    """Move the project FSM to the given status — for manual rollback or repair.

    Requires confirmation by default (`--yes` for quiet mode). Does not touch any
    artifact files: it only rewrites state.json. If you need to "wipe the project
    and start from scratch", delete the projects/<name>/ folder by hand.
    """
    project = _validate_project_name(args.project)
    target = args.to.strip().lower()
    if target not in _VALID_STATUSES:
        console.print(
            f"[red]❌ Invalid target status: {target!r}.[/red]\n"
            f"[white]Allowed: {', '.join(sorted(_VALID_STATUSES))}.[/white]"
        )
        sys.exit(2)

    state = load_state_safe(project)
    if state is None:
        console.print(f"[red]❌ state.json not found for project {project}.[/red]")
        sys.exit(1)

    old_status = state.status
    if old_status == target:
        console.print(f"[yellow]ℹ️ The project is already in status [bold]{target}[/bold] — nothing to change.[/yellow]")
        return

    if not args.yes:
        console.print(
            f"[yellow]⚠️ Current status: [bold]{old_status}[/bold] → new: [bold]{target}[/bold].[/yellow]\n"
            f"[white]Confirm the transition in [cyan]projects/{project}/state.json[/cyan][/white]"
        )
        try:
            answer = input("Continue? [y/N]: ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            console.print("[red]❌ Cancelled by user.[/red]")
            sys.exit(1)

    state.status = target
    # Reset active_agents to a sensible default for the new status.
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
        f"[green]✅ Status changed successfully.[/green]\n"
        f"[bold]{old_status}[/bold] → [bold yellow]{target}[/bold yellow]\n"
        f"Active agents: [white]{', '.join(state.active_agents)}[/white]\n\n"
        f"[white]Run [cyan]uv run cli.py status --project={project}[/cyan] to verify.[/white]",
        title="reset FSM",
        border_style="green",
    ))


# =====================================================================
# Main Argparse Parser
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Requirements Mind CLI — a next-generation requirements management tool built on the BMAD METHOD."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Commands")

    # init
    parser_init = subparsers.add_parser("init", help="Initialize a new project")
    parser_init.add_argument("--project", required=True, help="Name of the new project")
    parser_init.set_defaults(func=handle_init)

    # onboard
    parser_onboard = subparsers.add_parser("onboard", help="Record onboarding completion and move to Intake")
    parser_onboard.add_argument("--project", required=True, help="Project name")
    parser_onboard.set_defaults(func=handle_onboard)

    # intake
    parser_intake = subparsers.add_parser("intake", help="Record input parsing and check context.md")
    parser_intake.add_argument("--project", required=True, help="Project name")
    parser_intake.set_defaults(func=handle_intake)

    # draft
    parser_draft = subparsers.add_parser("draft", help="Record draft creation")
    parser_draft.add_argument("--project", required=True, help="Project name")
    parser_draft.add_argument("--doc", default="BRD", help="Document type (BRD/SRS/Tech-Design/API-Contract)")
    parser_draft.set_defaults(func=handle_draft)

    # validate
    parser_validate = subparsers.add_parser("validate", help="Read the validation report and advance the project")
    parser_validate.add_argument("--project", required=True, help="Project name")
    parser_validate.add_argument("--doc", default="BRD", help="Document type")
    parser_validate.add_argument("--version", type=int, default=1, help="Draft version")
    parser_validate.set_defaults(func=handle_validate)

    # final
    parser_final = subparsers.add_parser("final", help="Finalize an approved draft")
    parser_final.add_argument("--project", required=True, help="Project name")
    parser_final.add_argument("--doc", default="BRD", help="Document type")
    parser_final.add_argument("--version", type=int, required=True, help="Draft version")
    parser_final.set_defaults(func=handle_final)

    # analyze
    parser_analyze = subparsers.add_parser("analyze", help="Record a Mode B analytical task")
    parser_analyze.add_argument("--project", required=True, help="Project name")
    parser_analyze.add_argument("--task", required=True, help="The essence of the analytical investigation")
    parser_analyze.set_defaults(func=handle_analyze)

    # Augment: extend an existing document with artifacts (protected mode, see flows/09-augment.md)
    parser_augment = subparsers.add_parser(
        "augment",
        help="Run augment mode: extend an existing document with artifacts while preserving its structure"
    )
    parser_augment.add_argument("--project", required=True, help="Project name")
    parser_augment.add_argument("--baseline", required=True, help="Path to the baseline document (SRS/BRD/Tech-Design/API-Contract)")
    parser_augment.add_argument("--doc", required=True, help="Document type: BRD / SRS / Tech-Design / API-Contract")
    parser_augment.set_defaults(func=handle_augment)

    # collaborate
    parser_collaborate = subparsers.add_parser("collaborate", help="Print the instruction for Party Mode")
    parser_collaborate.add_argument("--project", required=True, help="Project name")
    parser_collaborate.add_argument("--agents", default="a2,a4", help="Comma-separated list of agent codes")
    parser_collaborate.set_defaults(func=handle_collaborate)

    # trace (Tier 1 deterministic ID validation)
    parser_trace = subparsers.add_parser(
        "trace",
        help="Tier 1 validation: linter for requirement IDs and traceability (no LLM)",
    )
    parser_trace.add_argument("--project", help="Project name (scans projects/<name>/draft/ and final/)")
    parser_trace.add_argument("--doc", choices=["BRD", "SRS", "Tech-Design", "API-Contract"], help="Filter by document type")
    parser_trace.add_argument("--version", help="Filter by version (without the v prefix)")
    parser_trace.add_argument("--file", help="Alternative to --project: path to a single .md file")
    parser_trace.set_defaults(func=handle_trace)

    # sync-vault
    parser_sync = subparsers.add_parser("sync-vault", help="Sync project folders with the Obsidian Vault")
    parser_sync.set_defaults(func=handle_sync_vault)

    # export-notebooklm
    parser_export = subparsers.add_parser("export-notebooklm", help="Export the project for NotebookLM")
    parser_export.add_argument("--project", required=True, help="Project name")
    parser_export.set_defaults(func=handle_export_notebooklm)

    # import-web
    parser_import = subparsers.add_parser("import-web", help="Headlessly import a page from Chrome (CDP) into input/")
    parser_import.add_argument("--project", required=True, help="Project name")
    parser_import.add_argument("--port", type=int, default=9222, help="Chrome debugging port (default 9222)")
    parser_import.add_argument("--query", required=True, help="Search query to find the tab (by URL or title)")
    parser_import.add_argument("--filename", default="confluence_specs.md", help="Output file name in the input/ folder")
    parser_import.set_defaults(func=handle_import_web)

    # setup-ide
    parser_setup = subparsers.add_parser("setup-ide", help="Set up local IDE AI-assistant folders for a new analyst")
    parser_setup.set_defaults(func=handle_setup_ide)

    # update
    parser_update = subparsers.add_parser("update", help="Update Requirements Mind to the latest version from GitHub")
    parser_update.set_defaults(func=handle_update)

    # status (diagnostics)
    parser_status = subparsers.add_parser("status", help="Show the current FSM status and project artifacts")
    parser_status.add_argument("--project", required=True, help="Project name")
    parser_status.set_defaults(func=handle_status)

    # reset (manual FSM control)
    parser_reset = subparsers.add_parser("reset", help="Force the FSM into the given status")
    parser_reset.add_argument("--project", required=True, help="Project name")
    parser_reset.add_argument(
        "--to",
        required=True,
        help="Target status: onboarding|intake|needs_questions|drafting|validating|needs_revision|approved",
    )
    parser_reset.add_argument("--yes", action="store_true", help="Do not prompt for confirmation")
    parser_reset.set_defaults(func=handle_reset)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)

if __name__ == "__main__":
    main()
