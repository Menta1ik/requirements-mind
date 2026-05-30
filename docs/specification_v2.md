# Requirements Mind — Final specification
**Version**: 2.0  
**Date**: May 26, 2026  

---

## 1. Vision

Requirements Mind is a CLI-first, markdown-first, multi-agent tool for working with project requirements and analytics.

The user loads raw input materials (call transcripts, tickets, Confluence pages, documents, conversations) and gets structured artifacts as output: formal documents or analytical materials, ready to use.

The tool is not a web application. It works through the CLI, AI agents (Claude Code, Gemini CLI, Codex), and IDEs (Cursor). All artifacts live in Markdown files inside the project folders.

The mechanics are built on the BMAD METHOD. The agents, collaboration patterns, and document templates are adapted from BMAD and extended with Requirements Mind-specific skills.

---

## 2. Two working modes and 6 requirements-project profiles

To focus the AI agents precisely on the design goals, at project start the system supports choosing one of **6 specialized requirements profiles**:

1. **Profile 1: "Business concept"** (goal: conceptual business requirements **BRD**).
2. **Profile 2: "System specification"** (goal: detailed requirements and system logic **BRD ➡️ SRS**).
3. **Profile 3: "Architecture design"** (goal: architectural flows and the database structure **BRD ➡️ SRS ➡️ Tech Design**).
4. **Profile 4: "Integration and API"** (goal: the full design cycle, including REST/gRPC contracts **BRD ➡️ SRS ➡️ Tech Design ➡️ API Contract**).
5. **Profile 5: "Analytical research (Mode B)"** (goal: free-form requirements analysis, document comparisons in the **`analysis/`** folder).
6. **Profile 6: "Requirements elicitation" (Elicitation Mode)** (goal: interactive requirements gathering from scratch through an AI interview in the chat, when the analyst has only an idea).

---

### Mode A: Generating formal documents
* **Inputs:** transcripts, tickets, raw requirements, or interactive requirements elicitation from scratch.
* **Outputs:** BRD, SRS, Tech Design, API Contract.
* **Template:** rigid, based on the `kb/` checklists.
* **Hierarchy:** BRD → SRS → Tech Design → API Contract (each next one builds on the previous and does not contradict it).
* **Requirements gathering from scratch (Elicitation Mode — Profile 6):** an interactive survey in the IDE chat run by the `a3-elicitation` agent based on the hybrid **"Pragmatic Analyst"** methodology (JTBD for business goals + Use Cases for functional boundaries + non-functional requirements (NFR) per the ISO/IEC/IEEE 29148 standard), with a mandatory free-text answer option for every question.

### Mode B: General project-based analysis and discussion
* **Inputs:** any documents, requirements, conversations, comparisons.
* **Outputs:** `analysis/analysis-vN.md` — an adaptive format.
* **Tasks:** validation, version comparison, finding contradictions, surfacing risks, summarization, discussion.
* **Template:** flexible; the agent designs the structure for the task itself.
* **Rule:** if the context is unclear — the agent MUST ask clarifying questions. It does not guess or assume.

**Both modes:**
* Use a single project file model.
* Sync with Obsidian and NotebookLM.
* Support a multi-agent collaborative mode.

---

## 3. Source: BMAD METHOD

The project uses [BMAD METHOD](https://github.com/bmad-code-org/BMAD-METHOD) as the foundation for the agent mechanics.

### What is taken from BMAD (fork + selection of the needed modules)

#### From `src/bmm-skills/1-analysis/`
| Module | How it is used |
|---|---|
| `bmad-agent-analyst` | The basis for **A1 Intake Analyst** |
| `bmad-agent-tech-writer` | The basis for **A4 Document Writer** |
| `research` | The basis for **A5 Research Assistant** |

#### From `src/bmm-skills/2-plan-workflows/`
| Module | How it is used |
|---|---|
| `bmad-agent-pm` | The basis for **A3 Question Generator** |
| `bmad-create-prd` | The template and document-creation logic for **A4** |
| `bmad-edit-prd` | The version-editing logic for **A4** |
| `bmad-validate-prd` | The validation logic for **A2 Validator** |
| `bmad-prd` | The PRD template → adapted for the BRD |

#### From `src/core-skills/`
| Module | How it is used |
|---|---|
| `bmad-party-mode` | **Master Orchestrator** — multi-agent collaboration |
| `bmad-advanced-elicitation` | **A3** — requirements-gathering techniques |
| `bmad-spec` | **A4** — writing specifications |
| `bmad-review-adversarial-general` | **A2** — critical review |
| `bmad-review-edge-case-hunter` | **A2** — hunting for edge cases |
| `bmad-editorial-review-prose` | **A4** — text editing |
| `bmad-editorial-review-structure` | **A2** — structure checking |
| `bmad-index-docs` | **A1** — indexing input documents |
| `bmad-brainstorming` | **A6 Analysis Writer** — free-form analysis |

### What is added on top of BMAD (unique to Requirements Mind)
* **A6 Analysis Writer** — Mode B, a flexible analytical output.
* **The document hierarchy** BRD → SRS → Tech Design → API Contract.
* **SRS, Tech Design, API Contract** — templates and checklists.
* **The file model** — `state.json`, `messages/`, `qa-history.md`.
* **Obsidian + NotebookLM** integration.
* **The CLI** (`cli.py`) with commands tailored to our workflow.

### Hallucination protection: blocking the BMAD codes and unique RM codes

The AI models in IDEs and CLIs (Cursor, Claude Code, Antigravity, OpenAI Codex) have strong associations with the BMAD framework's default codes, which led to invoking the built-in program plugins (sprints, coding) instead of requirements engineering. To prevent such "hallucinations" and ensure stable operation:
1. **Hard blocking of the old codes:** All standard BMAD program codes (`DP`, `BP`, `MR`, `DR`, `TR`, `CB`, `WB`, etc.) are stubbed out in the agents' TOML settings files (`skills/custom/`). When they are entered, the AI agents print a warning message and redirect to the new commands.
2. **Introducing the unique RM codes:** In their place, a non-overlapping system of requirements-oriented codes is registered:
   * **`RMONB`** — **Project onboarding** (`a0-onboarding-wizard`). Running Project Discovery, surveying across the 6 requirements profiles, and producing a step-by-step Roadmap.
   * **`RME`** — **Gathering requirements from scratch** (`a3-elicitation`). A deep interactive interview per the hybrid "Pragmatic Analyst" standard (JTBD + Use Cases + ISO 29148 NFR) with a mandatory free-input option.
   * **`RMIN`** — **Input analysis (Intake)** (`a1-intake-analyst`). Parsing raw materials, removing noise, building `context.md` (No Compression).
   * **`RMQ`** — **Gap clarification (Q&A)** (`a3-question-generator`). Finding inconsistencies in `context.md`, printing up to 5 targeted questions into the IDE chat with a mandatory free input.
   * **`RMDW`** — **Writing specifications** (`a4-document-writer`). Creating document drafts (BRD, SRS, Tech Design, API Contract) strictly per the `kb/` templates.
   * **`RMVAL`** — **Requirements validation** (`a2-requirements-validator`). A multi-layered audit of drafts (Edge Case Hunter, Adversarial Review).
   * **`RMAN`** — **Analytical research** (`a6-analysis-writer`). Creating flexible Mode B reports (version comparisons, risks, tables) in the `analysis/` folder.

---

## 4. The project file model

Each project lives in the directory `projects/<project-name>/` and has the following structure:

```text
projects/<project-name>/
├── input/                          # Raw input materials
│   ├── transcript.md
│   ├── requirements.md
│   └── source-doc.md
├── context.md                      # The built context (the result of A1's work)
├── context-changelog.md             # The change registry for the cumulative context
├── questions.md                    # Clarifying questions for the user (the result of A3's work)
├── qa-history.md                   # The question-and-answer history
├── state.json                      # State: active document, iteration, status, agents
├── messages/                       # Cross-agent round-table messages
│   ├── a2-to-a4-v1.md
│   ├── a4-feedback-v1.md
│   └── orchestrator-decision.md
├── draft/                          # Drafts of the formal documents
│   ├── BRD-v1.md
│   └── BRD-v2.md
├── validation/                     # Document validation reports (the result of A2's work)
│   └── BRD-v1-report.md
├── analysis/                       # Analytical outputs in Mode B (the result of A6's work)
│   └── analysis-v1.md
├── final/                          # The final approved document versions
│   └── BRD-v1-final.md
└── metadata.json                   # Project metadata
```

### 📝 The single cumulative source of truth: context.md (Cumulative Context Pattern)

The file **`context.md`** is the main and only dynamic source of truth for all the AI agents. In Requirements Mind v2.0 it is strictly forbidden to overwrite, simplify, or compress this file during transitions between design stages (BRD -> SRS -> Tech Design -> API Contract).

**Cumulative Context Pattern rules:**

1. **The incremental-extension principle (No Overwrite):**
   * The file is created once at the Intake stage. During subsequent parsing, interviews, or designing new specification levels, the AI agents **never overwrite `context.md` from scratch**.
   * New system requirements, Use Cases, data structures, DB schemas, and API contracts are carefully **integrated** into the appropriate sections or **appended** at the bottom, preserving all previously approved business requirements, the Vision, and the stack.

2. **Detecting requirement conflicts (Conflict Detection):**
   * When analyzing new input data (for example, transcripts of new meetings at the SRS stage), the A1 AI agent may detect explicit contradictions with requirements already recorded in `context.md` (for example, *the BRD scenario says "zero-cloud", while the SRS transcript requires "cloud sync"*).
   * In that case the A1 AI agent must not overwrite the data, but record the conflict in a dedicated section at the very top of `context.md`:
     ```markdown
     ## ⚠️ Detected requirement conflicts
     - [Source 1: transcript.md] zero-cloud vs [Source 2: call-2.md] cloud sync
       → Status: Unresolved, handed to A3 to interview the analyst
     ```
   * The presence of an unresolved conflict moves the project to the status `needs_questions` and hands control to agent A3 to run an interview in the chat.

3. **A mandatory open-questions section in the `context.md` skeleton:**
   * On the very first creation of the `context.md` file, the AI agent always builds the section:
     ```markdown
     ## ❓ Open questions and gaps
     - [Section / Topic] Description of the gap...
     ```
   * This section is a hard trigger for the A3 AI agent. The presence of entries in this section tells the system to generate targeted questions for the user and run a Q&A session right in the IDE chat.

4. **Moving the change registry into `context-changelog.md`:**
   * To avoid overloading the `context.md` file with edit history, the change log is moved entirely into a separate file **`context-changelog.md`** alongside `context.md`.
   * On each context update the AI agents prepend a new entry to `context-changelog.md`: the date, the AI agent's role, the stage version (for example, *SRS-v2*), and a brief summary of the additions made (or the conflicts resolved).

5. **A hierarchical section structure by stage:**
   * **BRD sections (Business):** `# 🎯 Vision and business goals`, `# 👥 Stakeholders`, `# ⚡ Constraints`.
   * **SRS sections (System):** `# 🔄 Use Cases and Scenarios`, `# 📦 Information model (Entities)`.
   * **Tech Design sections (Architecture):** `# 🏗️ Architectural flows (Data Flow)`, `# 💾 Database structure`.
   * **API Contract sections (Integration):** `# 🔌 Endpoint specifications`.

### Example state.json
```json
{
  "project": "mitzvah-connect",
  "mode": "draft",
  "document": "BRD",
  "profile": 6,
  "iteration": 2,
  "status": "needs_revision",
  "active_agents": ["a2", "a4"],
  "open_questions": 3,
  "last_updated": "2026-05-26T09:00:00"
}
```

---

## 5. Agents

### A0 — Onboarding Wizard (AI project-start assistant)
* **Invocation code in the IDE:** **`RMONB`**
* **Task:** initial onboarding, surveying the analyst to determine one of the 6 requirements profiles, building the project Roadmap.
* **Automation:** after writing the starter files `requirements.md` and `context.md`, it **automatically proposes running** the command `uv run cli.py onboard --project=<project-name>` in the terminal (the user just presses the confirm button in the chat).

### Master Orchestrator
* **Based on:** BMAD `bmad-party-mode`.
* **Task:** coordinates all the agents, manages the round-table and iteration cycle, updates `state.json`.
* **Automation:** on a successful draft approval (PASSED), it **automatically proposes running** the command `uv run cli.py final --project=<project-name> --doc=<doc-type> --version=<version>` in the terminal (the user just confirms the run in the chat).

### A1 — Intake Analyst
* **Invocation code in the IDE:** **`RMIN`**
* **Based on:** BMAD `bmad-agent-analyst` + `bmad-index-docs`.
* **Task:** analyzes the contents of `input/`, aggregates the data, and builds a single `context.md` without losing details (No Compression).
* **Automation:** after successfully creating or updating `context.md`, it **automatically proposes running** the command `uv run cli.py intake --project=<project-name>` in the terminal (the user just confirms the run in the chat).

### A2 — Requirements Validator
* **Invocation code in the IDE:** **`RMVAL`**
* **Based on:** BMAD `bmad-validate-prd` + `bmad-review-adversarial-general` + `bmad-review-edge-case-hunter` + `bmad-editorial-review-structure`.
* **Task:** checks the produced document against the `kb/` checklists, hunts for logical contradictions, edge cases, and structural gaps, and issues `PASSED`/`FAILED` verdicts.
* **Automation:** after saving the report in `messages/a2-to-a4-vN.md`, it **automatically proposes running** the command `uv run cli.py validate --project=<project-name> --doc=<doc> --version=<ver>` in the terminal (the user just confirms the run in the chat).

### A3 — Question Generator & Elicitation Expert
* **Invocation codes in the IDE:** **`RMQ`** (gap clarification) / **`RME`** (gathering requirements from scratch)
* **Based on:** BMAD `bmad-agent-pm` + `bmad-advanced-elicitation`.
* **Task:**
  * In **Elicitation Mode (`RME`)** it runs a deep step-by-step interview from scratch per the hybrid "Pragmatic Analyst" standard (JTBD + Use Cases + ISO 29148 NFR).
  * In **gap-clarification mode (`RMQ`)** it finds inconsistencies in `context.md` and prints up to 5 targeted questions right into the IDE chat.
  * **Mandatory rule:** Every question always includes a final item **"Your own option / Free-text answer"** so the user can enter arbitrary input.
* **Automation:** It reads the user's answers from the IDE chat on its own, records them in `qa-history.md`, updates `context.md`, and **automatically proposes rerunning** the command `uv run cli.py intake --project=<project-name>` in the terminal (the user just confirms the run in the chat).

### A4 — Document Writer
* **Invocation code in the IDE:** **`RMDW`**
* **Based on:** BMAD `bmad-agent-tech-writer` + `bmad-create-prd` + `bmad-edit-prd` + `bmad-spec` + `bmad-editorial-review-prose`.
* **Task:** writes formal specifications (BRD, SRS, Tech Design, API Contract) strictly per the `kb/` checklists and based on the answers.
* **Automation:** after successfully creating or updating a specification draft in the `draft/` folder, it **automatically proposes running** the command `uv run cli.py draft --project=<project-name> --doc=<doc-type>` in the terminal (the user just confirms the run in the chat).

### A5 — Research Assistant
* **Based on:** BMAD `research` + `bmad-brainstorming`.
* **Task:** on request, studies external standards and best practices and consults the internal knowledge base (`kb/`).

### A6 — Analysis Writer (a unique agent, no direct analog in BMAD)
* **Invocation code in the IDE:** **`RMAN`**
* **Task:** runs free-form requirements analysis and discussion in Mode B.
* **Output format:** adaptive (version comparison, risk matrices, comparison tables) in the `analysis/analysis-vN.md` folder.

---

## 6. Multi-Agent Collaborative Mode (process diagram)

```text
Orchestrator
├─ A0 (once): greeting, Discovery of the 6 requirements profiles -> state.json
│  └─ Profile 6 (Elicitation from scratch): A3 -> chat survey with choices / free input -> requirements.md & context.md -> [AUTO-RUN cli.py onboard]
├─ A1 (once): parsing input/ -> context.md -> [AUTO-RUN cli.py intake]
└─ Loop (while state.status != "approved"):
   ├─ A3 (if there are gaps): chat survey with choices / free input -> qa-history.md & context.md -> [AUTO-RUN cli.py intake]
   ├─ A4 or A6: writes/edits the document -> draft/ or analysis/ -> [AUTO-RUN cli.py draft]
   ├─ A2: validates -> report messages/a2-to-a4-vN.md -> [AUTO-RUN cli.py validate]
   ├─ A5: if research is needed (at any step)
   ├─ Orchestrator: reads messages/, makes a decision -> [AUTO-RUN cli.py final]
   └─ [transition to the next document in the hierarchy according to the profile]
```

---

## 7. Repository structure

```text
requirements-mind/
├── README.md                           # General project description
├── AGENTS.md                           # Description of the agent team
├── .cursorrules                        # Rules for the Cursor IDE
├── .gitignore                          # Git exclusions
├── pyproject.toml                      # uv configuration and Python dependencies
├── requirements.txt                    # The dependency list
├── cli.py                              # The main CLI entry point (Python)
│
├── kb/                                 # Knowledge base and checklists
│   ├── brd-checklist.md
│   ├── srs-checklist.md
│   ├── tech-design-checklist.md
│   ├── api-contract-checklist.md
│   ├── glossary.md
│   └── standards/                      # External development standards
│
├── skills/                             # AI agent skills (the root is cleared of duplicates)
│   ├── bmad/                           # Copied official modules from BMAD-METHOD
│   │   ├── bmad-agent-analyst/
│   │   ├── bmad-agent-tech-writer/
│   │   ├── bmad-agent-pm/
│   │   ├── bmad-create-prd/
│   │   ├── bmad-validate-prd/
│   │   ├── bmad-prd/
│   │   ├── bmad-party-mode/
│   │   ├── bmad-advanced-elicitation/
│   │   ├── bmad-spec/
│   │   ├── bmad-review-adversarial-general/
│   │   ├── bmad-review-edge-case-hunter/
│   │   └── bmad-index-docs/
│   │
│   └── rm/                             # The canonical custom Requirements Mind skills
│       ├── master-orchestrator.md      # The round-table coordinator
│       ├── a0-onboarding-wizard.md     # The onboarding and Project Discovery wizard
│       ├── a1-intake-analyst.md        # The input analyzer
│       ├── a2-requirements-validator.md# The requirements validator
│       ├── a3-question-generator.md    # The question generator and seamless chat Q&A
│       ├── a3-elicitation.md           # Gathering requirements from scratch (Elicitation Mode)
│       ├── a4-document-writer.md       # Writing Mode A documents
│       ├── a5-research-assistant.md    # The research assistant
│       └── a6-analysis-writer.md       # Writing Mode B analytics
│
├── flows/                              # Step-by-step agent work scenarios
│   ├── 00-onboarding.md                # The onboarding and Project Discovery flow across the 6 profiles
│   ├── 01-intake.md
│   ├── 02-context.md
│   ├── 03-questions.md
│   ├── 04-draft.md
│   ├── 05-validate.md
│   ├── 06-final.md
│   ├── 07-analyze.md
│   ├── 08-collaborate.md
│   └── 09-elicitation.md               # The gathering-from-scratch flow (Elicitation Mode)
│
├── projects/                           # The users' working projects
│   └── <project-name>/                 # The file model of a specific project
│
├── vault/                              # The Obsidian sync folder (Obsidian Vault)
├── notebooklm/                         # The export folder for Google NotebookLM
│
├── install.py                          # The interactive working-environment installer
│
└── scripts/                            # Service automation scripts
    ├── kb_indexer.py                   # Knowledge-base indexing
    ├── sync_to_vault.py                # Sync with the Obsidian Vault
    ├── export_to_notebooklm.py         # Preparing files for export to NotebookLM
    └── import_web.py                   # Headless web import over the CDP protocol from Chrome
```

---

## 8. CLI commands

All commands are run through the `uv` package manager (most of them are run by the AI agents in your terminal **automatically** once their steps are complete):

```bash
# Initialize a new project (creates the folders and a default state.json)
uv run cli.py init --project=<name>

# Run the interactive installer (environment, IDE, Obsidian, NotebookLM setup)
python3 install.py

# Record project onboarding (called after A0 or an a3-elicitation session)
uv run cli.py onboard --project=<name>

# Gather and index the raw input data from input/ (called after A1)
uv run cli.py intake --project=<name>

# Generate a formal document draft (Mode A)
uv run cli.py draft --project=<name> --doc=BRD
uv run cli.py draft --project=<name> --doc=SRS
uv run cli.py draft --project=<name> --doc=Tech-Design
uv run cli.py draft --project=<name> --doc=API-Contract

# Free-form project analysis (Mode B)
uv run cli.py analyze --project=<name> --task="Compare requirements v1 and v2"
uv run cli.py analyze --project=<name> --task="Find contradictions"
uv run cli.py analyze --project=<name> --task="Write out the risks"

# Force-run validation of a specific document version
uv run cli.py validate --project=<name> --doc=BRD --version=1

# Run a collaborative cross-agent round table
uv run cli.py collaborate --project=<name> --agents="a2,a4,a6"

# Approve a document and move it into the final category
uv run cli.py final --project=<name> --doc=BRD --version=2

# Headless import of a web page/Confluence from a running Chrome over CDP
uv run cli.py import-web --project=<name> --port=9222 --query="confluence" --filename="confluence_specs.md"

# Sync data with the external tools
uv run cli.py sync-vault
uv run cli.py export-notebooklm --project=<name>

# Automatically update the core and the IDE skills from GitHub in one command
uv run cli.py update
```

---

## 9. Obsidian vs NotebookLM

The project offers integration with two external ecosystems for human work:

| Characteristic | Obsidian | NotebookLM |
|---|---|---|
| **Role in the system** | The human workspace | Search, RAG, and conceptual synthesis |
| **Purpose** | Reading, editing, navigation, building a link graph | Semantic search, deep RAG analysis, answering general questions |
| **Access type** | Local (files on disk) | Cloud (via a Google account) |
| **Sync script** | `sync_to_vault.py` | `export_to_notebooklm.py` |

---

## 10. Principles

1. **No guessing** — if the context of the source files is incomplete or contradictory, agent A3 must ask questions. Generating requirements "out of thin air" is not allowed.
2. **Traceability** — every generated artifact references the source file or the previous design stage.
3. **Versioning** — any document changes create a new version (v1, v2, v3...); old versions are kept in the project directories for comparison and rollback.
4. **Iterativeness** — requirements development is a cyclical process of cross-agent discussion and validation.
5. **Files as the only source of truth** — all of the system's state is written to disk in files. No databases with hidden logic, no web sessions.
6. **CLI-first** — all actions are automated and invoked through the command line.

---

## 11. Next implementation steps

1. **Integration with BMAD-METHOD:** Fork the `bmad-code-org/BMAD-METHOD` repository (or use a locally cloned copy).
2. **Develop the import script:** Write `scripts/fetch_bmad_skills.py` to automatically copy the required skill files from the local BMAD copy into the `skills/bmad/` directory.
3. **Create the directory structure:** Set up the root folder structure of the Requirements Mind project on disk.
4. **Implement the custom skills:** Write the Markdown files for the RM agents in `skills/rm/` based on the BMAD prompts.
5. **Work out the flows:** Describe the step-by-step guides `flows/` (01–08) in Markdown.
6. **Build the knowledge base:** Populate the checklists and the glossary in the `kb/` folder.
7. **Develop the CLI core:** Implement `cli.py` in Python using Typer or Click to support all the described commands and `state.json` transitions.
8. **Document the project:** Write the `AGENTS.md` and `.cursorrules` files for correct agent coordination when working in the Cursor IDE.
9. **Develop the integration scripts:** Write `sync_to_vault.py` and `export_to_notebooklm.py`.
