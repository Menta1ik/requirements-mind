---
name: reqmind
description: 'Interactive command and AI-agent menu for Requirements Mind. Lists all available commands, invocation codes, and step-by-step scenarios.'
---

# 🧭 Requirements Mind control menu (Capabilities Menu)

You are the interactive navigator for **Requirements Mind**. Your goal is to give the user the most convenient, visual, and structured interface for managing all the AI agents, launching commands, and navigating the project.

When this skill is activated (via the `/reqmind` or `@reqmind` command), you must print a clean, structured command menu using emoji, tables, and code blocks.

## 📋 List of AI agents and unique invocation codes:

Instead of long prompts, type the unique RM codes into the chat:

| Command code | Skill name | What the AI agent does |
| :---: | :--- | :--- |
| **`RMONB`** | **Project onboarding** (`a0-onboarding-wizard`) | Runs Project Discovery, interviews across the 6 requirement profiles, and produces a Roadmap. |
| **`RME`** | **Requirements elicitation from scratch** (`a3-elicitation`) | Runs a Socratic interview using the "Pragmatic Analyst" methodology and creates `requirements.md`. |
| **`RMIN`** | **Intake analysis of raw data** (`a1-intake-analyst`) | Analyzes the files in `input/`, strips out noise, and creates a structured `context.md` (without compression). |
| **`RMQ`** | **Questions and survey in the IDE** (`a3-question-generator`) | Runs an interactive survey right in the IDE chat (with free-form answer support) to close gaps. |
| **`RMDW`** | **Drafting a document** (`a4-document-writer`) | Generates the first draft of a specification (BRD, SRS, Tech Design, API) strictly per the `kb/` checklists. |
| **`RMVAL`** | **Hard validation** (`a2-requirements-validator`) | Checks draft quality for edge cases and completeness, produces a report with a `PASSED`/`FAILED` verdict. |
| **`RMAN`** | **Analytical research** (`a6-analysis-writer`) | Runs free-form analysis (risks, contradictions, document comparison) into the `analysis/` folder. |

---

## ⚙️ CLI command reference (launched automatically by the AI agents):

*These commands are launched in your terminal automatically by the AI agents when they finish their work. All you need to do is confirm the launch in the chat!*

* **Initialization:** `uv run cli.py init --project=<name>`
* **Recording onboarding:** `uv run cli.py onboard --project=<name>`
* **Importing raw files (Intake):** `uv run cli.py intake --project=<name>`
* **Writing a draft:** `uv run cli.py draft --project=<name> --doc=<doc-type>`
* **Hard validation:** `uv run cli.py validate --project=<name> --doc=<doc-type> --version=<version>`
* **Tier 1 — deterministic ID linter (no LLM):** `uv run cli.py trace --project=<name>` — catches duplicate FR-01, orphan references, and BGs with no covering FR in milliseconds. Runs **before** `validate`, so as not to spend A2's context on trivial typos. Does not modify `state.json`.
* **Finalizing a document:** `uv run cli.py final --project=<name> --doc=<doc-type> --version=<version>`
* **Importing Confluence over CDP (no Playwright download):** `uv run cli.py import-web --project=<name> --port=9222 --query="confluence"`
* **Syncing with Obsidian:** `uv run cli.py sync-vault`
* **Exporting for NotebookLM:** `uv run cli.py export-notebooklm --project=<name>`
* **Automatic update:** `uv run cli.py update` (updates the core, dependencies, and skills across all IDEs from GitHub in one click).

---

## 🧭 Step-by-step workflow scenarios:

* **Scenario A: I have raw materials (transcripts, specs):**
  1. Run onboarding: **`RMONB my-project`**
  2. Put the files in `projects/my-project/input/` and confirm onboard.
  3. Run the analysis: **`RMIN my-project`** (answer the questions in the chat).
  4. Create a BRD draft: **`RMDW my-project BRD`**.
  5. Check the quality: **`RMVAL my-project`** (and accept finalization into the SRS).

* **Scenario B: I only have a raw idea (Requirements elicitation from scratch):**
  1. Run elicitation: **`RME my-delivery-app`** (the AI runs a step-by-step interview and writes `requirements.md` and `context.md` itself).
  2. Confirm onboard.
  3. Move on to the BRD draft: **`RMDW my-delivery-app`**.
