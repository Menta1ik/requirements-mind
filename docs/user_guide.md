# User guide: Requirements Mind v2.0 (IDE-Native)

Requirements Mind is a professional tool for working with requirements, designed for systems analysts, business analysts, and product managers.

In version 2.0 the tool uses the **IDE-Native AI Agents** philosophy built on the **BMAD METHOD** framework. This means that:
1. **The execution engine for the AI is your own AI assistant in the development environment or terminal** — for example, Cursor, Claude Code, Antigravity, or OpenAI Codex. They already have access to the best models and to your context.
2. **The CLI tool (`cli.py`) acts as a pure file and state controller (Pure State & File Controller).** It requires no API keys, runs locally, validates state transitions in `state.json`, and syncs the project with the external Obsidian and NotebookLM environments.
3. **A cumulative source of truth (Cumulative Context Pattern):** The main context file `context.md` is never overwritten from scratch during pipeline transitions (BRD ➡️ SRS ➡️ Tech Design), nor is it compressed. New Use Cases, entities, database structures, and endpoints are carefully embedded by the AI agents into the appropriate sections, preserving all previously approved business requirements, the Vision, and the stack, while a change log (registry) is automatically maintained in a separate file `context-changelog.md` alongside it.

---

## 0. Initial setup (interactive installer)

For maximum simplicity and automation of deploying an analyst's working environment from scratch in any folder on your computer, run a single command in the terminal — pick the block for your OS.

**🍎 macOS / 🐧 Linux (Bash / Zsh):**
```bash
curl -fsSL https://raw.githubusercontent.com/Menta1ik/requirements-mind/main/install.py -o install.py && python3 install.py
```

**🪟 Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Menta1ik/requirements-mind/main/install.py -OutFile install.py; python install.py
```

> **Required on Windows:** Python 3.10+ (`python --version`), Git, and PowerShell 5.1+ (built into Windows 10/11).
> If `python` is not found — install Python from [python.org](https://www.python.org/downloads/) and check the **"Add Python to PATH"** box.

*(Or, if you have already cloned the repository locally, run `python3 install.py` on macOS/Linux or `python install.py` on Windows in the root folder.)*

**What the installer does:**
1. **Checks the system:** the correct Python version (>= 3.10 required) and the presence of Git.
2. **Sets up the virtual environment:** detects whether the ultra-fast `uv` manager is present, creates a local `.venv` environment, and installs the required dependencies from `requirements.txt`.
3. **Links the AI skills to your IDE/CLI:** copies all the necessary agent scripts into the service folders of the AI assistants you choose (Cursor, Claude Code, Google Antigravity, OpenAI Codex).
4. **Sets up integrations:** creates the necessary folders for the Obsidian Vault and prepares the structure for Google NotebookLM.
5. **Deploys a demo project:** automatically creates a `demo-project` and exports a ready JSON file to `notebooklm/demo-project.json`, so you can test the whole system instantly!

---

## 1. The 6 target requirements-project profiles

When creating a project, the system helps you choose one of **6 specialized requirements profiles**, depending on your project's goals:

* **Profile 1: "Business concept"** (goal: conceptual business requirements **BRD**).
* **Profile 2: "System specification"** (goal: detailed requirements and system logic **BRD ➡️ SRS**).
* **Profile 3: "Architecture design"** (goal: architectural flows and the database structure **BRD ➡️ SRS ➡️ Tech Design**).
* **Profile 4: "Integration and API"** (goal: the full design cycle, including REST/gRPC contracts **BRD ➡️ SRS ➡️ Tech Design ➡️ API Contract**).
* **Profile 5: "Analytical research (Mode B)"** (goal: free-form requirements analysis, document comparisons in the **`analysis/`** folder).
* **Profile 6: "Requirements elicitation" (Elicitation Mode)** (goal: gathering requirements from scratch through an AI interview in the chat, when the analyst has only an idea).

---

## 2. The unique AI command codes (Capabilities Menu) in the IDE chat

Instead of writing long prompts in the IDE chat, use the letter codes to invoke the skill you need. The AI recognizes them automatically:

> [!WARNING]
> All standard BMAD program codes (such as `DP`, `BP`, `MR`, `DR`, `TR`, `CB`, `WB`, etc.) are **fully blocked and stubbed out** to prevent conflicts and AI-model hallucinations. Use only the unique `RM...` codes:

* **`RMONB`** — **Start project onboarding** (`a0-onboarding-wizard`). Helps run Project Discovery, surveys you across the 6 requirements profiles, and produces a step-by-step Roadmap.
* **`RME`** — **Start gathering requirements from scratch** (`a3-elicitation`). Launches a deep-interview session per the "Pragmatic Analyst" standard (JTBD + Use Cases + ISO 29148) and creates `requirements.md`.
* **`RMIN`** — **Start Intake analysis** (`a1-intake-analyst`). Analyzes the files in `input/`, removes noise, and creates `context.md` (without compressing the data).
* **`RMQ`** — **Generate clarifying questions** (`a3-question-generator`). Runs the survey right in the IDE chat (with free-input support) to close gaps in the context.
* **`RMDW`** — **Write a specification draft** (`a4-document-writer`). Generates the first draft of a document (BRD, SRS, Tech Design, API Contract) strictly per the `kb/` knowledge-base checklists.
* **`RMVAL`** — **Run quality control** (`a2-requirements-validator`). Checks the draft for edge cases and completeness, and produces a report with a `PASSED`/`FAILED` verdict.
* **`RMAN`** — **Start an analytical investigation** (`a6-analysis-writer`). Runs a free-form analysis (risks, contradictions, document comparison) into the `analysis/` folder.
* **`RMAUG`** — **Start extending an existing document** (Augment Mode). You already have an SRS/BRD/Tech-Design/API-Contract and need to **carefully extend** it with new artifacts (a meeting transcript, updated BRs, notes), **preserving the structure and wording** of the baseline. The AI must show a diff plan in the chat and wait for your confirmation **before** writing a new version. See the [detailed walkthrough](walkthroughs/augment-dams-srs.md).
* **`reqmind`** — **Interactive control menu** (`reqmind`). Displays a clear interactive cheat sheet of all available RM codes, CLI commands, and step-by-step scenarios.

> [!TIP]
> **The interactive navigator `/reqmind`:** By typing the command **`/reqmind`** in the IDE chat (in Claude Code / Antigravity) or by mentioning **`@reqmind`** (in Cursor), you instantly get a nice Capabilities Menu from which you can invoke any agent or view the list of all the steps!

*All the AI agents are trained to **run the needed CLI command on their own** in your IDE terminal once their work is done! All you have to do is confirm the run in the IDE chat.*

### 🗣️ Command input formats in the IDE chat
You can talk to the AI in whatever format is convenient:
1. **As an ordinary word in a sentence:** the AI automatically extracts the unique code from your text request (for example: *"Mary, hi! Run RME for the new project delivery-app"*).
2. **As a short "shot command":** just send the code and the project name to the chat (for example: `RMONB my-project`).
3. **With a slash (`/`):** if you are used to slash commands (for example: `/RMONB my-project`).

### 🔍 Integrating the RM codes into the slash menu and IDE autocomplete

#### 1. In the Cursor IDE (via the `@` At-Mentions mechanism)
In the Cursor IDE, the built-in dropdown for the slash (`/ask`, `/edit`, etc.) is hard-wired into the program's core. But Cursor offers an incredibly convenient alternative — the **`@` (At-Mentions)** menu:
1. Type the **`@`** symbol in the input line.
2. In the list of files and folders that appears, start typing the name of the skill you need, for example: **`@a0-onboarding-wizard`** or **`@a3-elicitation`**.
3. Attach this skill to the chat and send a message (for example: *"Run for my-project"*). The AI will apply this skill with 100% accuracy!

#### 2. In the Google Antigravity SDK and Claude Code (automatically via `/`)
Since our `install.py` installer copied the script files into the `.agent/skills/` and `.claude/skills/` service folders, the AI assistants **automatically index their titles**. When you type a slash (**`/`**) in the chat input line, these commands with their descriptions appear in the autocomplete dropdown!

---

## 3. Step-by-step work scenarios

### Scenario A: Gathering requirements from scratch (Elicitation Mode — Profile 6)
Used when there is no project yet and you have only a raw idea in your head.

#### Step A1: Start gathering requirements in the IDE chat (initialization and interview)
1. Open a chat with the AI assistant in the IDE or launch it in the CLI (Cursor, Claude Code, Antigravity, OpenAI Codex).
2. Tell the AI agent Mary:
   > **"Mary, hi! Run RME for the new project my-delivery-app"**
3. The AI agent will **create the project folder structure on disk on its own**, generate the state file `state.json`, and immediately start a step-by-step dialogue based on the hybrid **"Pragmatic Analyst"** methodology:
   * **Business goals (JTBD):** the AI helps formulate Jobs-to-be-Done (for example: *"When I want to place an order, I want to see the status, so that..."*).
   * **Boundaries and Use Cases:** the AI asks about user roles and identifies the functional blocks (Catalog, Orders, Couriers).
   * **System NFRs (per ISO 29148):** the AI surfaces requirements for security, integrations, and load.
   * **Free-text answer:** for every question the AI always leaves a free-text option ("Your own option"), so you can describe your thoughts in your own words.
4. At the end of the interview the AI will build and save to disk on its own:
   * `projects/my-delivery-app/input/requirements.md` — the structured requirements.
   * `projects/my-delivery-app/context.md` — the starter context file.
5. The AI agent will **automatically run** the command in the terminal:
   ```bash
   uv run cli.py onboard --project=my-delivery-app
   ```
   *(All you have to do is press the confirm button in the IDE chat.)*

---

### Scenario C: Headless import of requirements from closed web resources (Confluence/Jira)

Used when the source materials or specifications live in a corporate Confluence or Jira knowledge base or on web pages protected by a corporate VPN, SSO, or 2FA.

#### Step C1: Prepare the Google Chrome browser
So that the AI agent can read the data without having to enter passwords or bypass two-factor authentication (2FA), we connect to your running browser:

1. **Fully close Chrome:**
   * macOS — **Cmd + Q**.
   * Windows / Linux — close all Chrome windows and make sure it is not in the tray/processes (Task Manager → end all `chrome.exe`).

2. **Launch Chrome from the terminal with a remote debugging port** — pick the block for your OS:

   **🍎 macOS:**
   ```bash
   open -a "Google Chrome" --args --remote-debugging-port=9222
   ```

   **🐧 Linux:**
   ```bash
   google-chrome --remote-debugging-port=9222
   # or: chromium --remote-debugging-port=9222
   ```

   **🪟 Windows (PowerShell):**
   ```powershell
   Start-Process "chrome.exe" -ArgumentList "--remote-debugging-port=9222"
   ```
   > If `chrome.exe` is not in PATH, give the full path:
   > `Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222"`

3. In that window, open the tab with the Confluence article or Jira ticket you want to extract requirements from.

#### Step C2: Request an automatic import in the IDE/CLI chat
1. Write to your AI assistant in the IDE chat or launch it in the CLI (Cursor, Claude Code, Antigravity, OpenAI Codex):
   > **"Mary, import the specification from the Confluence tab for the project my-app"**
2. The AI agent instantly recognizes the request and **runs the import command ON ITS OWN** in the terminal:
   ```bash
   uv run cli.py import-web --project=my-app --port=9222 --query="confluence" --filename="confluence_specs.md"
   ```
   *(All you have to do is press the confirm-run button in the IDE chat or terminal.)*
3. The local Python script `scripts/import_web.py` connects to your Chrome over the CDP protocol, finds the right tab, downloads its HTML, converts it into clean Markdown (stripping web clutter: headers, side menus, widgets), and carefully saves it into `projects/my-app/input/confluence_specs.md`.

After that, the AI agent automatically continues the standard input-parsing pipeline (`RMIN`).

> [!TIP]
> **Architectural detail (no browser downloads):**
> Because the import goes through a connection to a running Chrome (`CDP`), you do **NOT NEED** to download the Playwright browser binaries (via `playwright install`). The script uses your working Chrome on the same machine, which provides high speed, disk savings, and an automatic bypass of logins and VPNs.

---

### Scenario B: The standard pipeline (Profiles 1–5, raw data exists)
The document generation chain: `BRD` (business requirements) → `SRS` (technical specifications) → `Tech Design` (architecture design) → `API Contract` (API specification).

#### Step B1: Automatic initialization and file preparation
1. Just tell Mary in your IDE chat:
   > **"Mary, hi! Run RMONB for the new project my-app"**
2. The AI agent will **create the project folder structure on disk on its own** and build the state file `state.json`.
3. Place your raw files (transcripts, specs, ticket lists) into the automatically created folder `projects/my-app/input/`.
4. Answer the onboarding-interview questions in the chat, after which the AI agent will automatically propose and run the onboarding-completion command:
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py onboard --project=my-app
   ```

#### Step B2: Initial parsing (Intake)
1. Ask the AI assistant in the IDE:
   > **"Mary, run RMIN for the project my-app"**
2. The AI analyzes the inputs, creates `context.md`, and **proposes running the parsing command (Intake) on its own**:
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py intake --project=my-app
   ```
* **Completeness check:** the CLI automatically checks `context.md`.
  * If an **incompleteness flag for the requirements** is detected → the status changes to `needs_questions`. The A3 AI agent automatically prints up to 5 questions right into the IDE chat with answer options and a mandatory free-input item. You answer in the chat, the AI writes the answers into `qa-history.md` itself, updates `context.md`, and automatically proposes rerunning Intake.
  * If the context is complete → the status changes to `drafting`.

#### Step B3: Generating a specification draft (Draft)
1. Ask the AI assistant in the IDE:
   > **"John, run RMDW for the project my-app"** (specify the document type you need, for example, BRD).
2. The AI creates the draft `projects/my-app/draft/BRD-v1.md` per the `kb/` checklists and **automatically proposes running the draft-recording command**:
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py draft --project=my-app --doc=BRD
   ```
The project status changes to `validating`.

#### Step B4: Quality control (validation)

Validation in Requirements Mind is two-tier. First — the cheap deterministic form linter (Tier 1, no LLM), then — the semantic LLM check from A2 (Tier 2).

**B4.0 (optional, but useful): Tier 1 — the ID and traceability linter.**
```bash
uv run cli.py trace --project=my-app
# or a single document:
uv run cli.py trace --project=my-app --doc=BRD --version=1
```
In milliseconds the linter catches:
* duplicate IDs (`FR-01` defined twice);
* orphan references (`FR-15` is mentioned in the SRS but defined nowhere);
* Business Goals from the BRD without FR coverage in the SRS;
* ID format violations (`FR_01`, `fr-01`, `FR-01234567`).

It does not touch `state.json` — it is a pure form check. **If there are errors (exit code 1)** — fix them before running the expensive LLM validator, otherwise A2 will spend its context on trivial typos instead of meaning. The linter is suitable for embedding into a pre-commit hook or CI.

**B4.1: Tier 2 — RMVAL (semantic LLM validation).**
1. Ask the AI assistant in the IDE:
   > **"John, run RMVAL for the project my-app"** (the AI will run the A2 validator, write a report into `messages/a2-to-a4-v1.md`, and **automatically propose running the validation command**):
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py validate --project=my-app --doc=BRD --version=1
   ```
* **If FAILED:** the status changes to `needs_revision`. Ask the AI to fix the draft via `RMDW` based on the findings in the report.
* **If PASSED:** the status changes to `approved`.

#### Step B5: Finalization and advancing along the chain (Final)
After approval, the AI agent **proposes running the finalization command on its own** in your terminal:
```bash
# RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
uv run cli.py final --project=my-app --doc=BRD --version=1
```
The CLI copies the document into `projects/my-app/final/BRD-v1-final.md` and moves the project on to preparing the next document in the chain — the SRS (technical specification). On the next cycle the AI automatically takes the approved `BRD-v1-final.md` as the input for the SRS.

---

### Scenario D: Extending an existing document with artifacts (Augment Mode)

Used when **a formal document (SRS / BRD / Tech-Design / API-Contract) already exists and is agreed upon**, and new artifacts have come in (a meeting transcript, updated BRs, notes) with which it needs to be **extended without rebuilding the structure**.

> ⚠️ **When NOT to use augment:** if the baseline document is outdated/incorrect and you deliberately need to rewrite it — use the regular `Scenario B` (draft from scratch). Augment is precisely about "keep as is and extend".

**The key difference from a regular draft:** A4 (Document Writer) works in **protected augment mode** — it must show you a diff plan in the chat and get explicit confirmation before writing a new version of the document. The baseline's structure, the wording of requirements, and the field and entity names of the data models are inviolable without your separate OK.

#### Step D1: Launch augment mode

1. Place the baseline document in any folder on disk (for example, `path/to/SRS-v1.md`).
2. In the terminal, run:
   ```bash
   uv run cli.py augment \
     --project=my-app \
     --baseline=path/to/SRS-v1.md \
     --doc=SRS
   ```
3. The CLI copies the baseline into `projects/my-app/input/baseline/SRS-v1.md`, creates `context.md` with the frontmatter `rm_mode: augment`, and moves the project to `status: drafting, mode: augment`.

#### Step D2: Place the artifacts in input/

Place all the enrichment artifacts (transcripts, updated BRs, notes) into `projects/my-app/input/` — **in the root of the folder, NOT in the `baseline/` subfolder**.

#### Step D3: A1 parses the artifacts into a delta

Write to the AI in the IDE chat:
> **"Mary, run RMIN for the project my-app. This is augment mode, the baseline is `input/baseline/SRS-v1.md`. Do not dissolve the baseline into `context.md`, describe only the delta from the artifacts."**

A1 writes a **"🔄 Delta to extend the baseline"** section into `context.md` with a list of the new facts from the artifacts and a mapping of "where to embed them in the baseline". Next — the standard command:
```bash
uv run cli.py intake --project=my-app
```

#### Step D4: A4 shows the diff plan and waits for your OK

> **"John, run RMAUG for the project my-app. Show me the diff plan and wait for my confirmation before writing the new version."**

A4 prints a structured plan into the chat: what it will add as **new**, what it will **change** in the existing sections (with justification and a reference to the artifact), and which sections it will keep **1:1**.

⚠️ **Important:** if A4 skipped the diff-plan phase and wrote the file straight away — that is a contract violation. Roll back and ask again. The Master Orchestrator will return the document to `needs_revision`, but checking with your own eyes is more reliable.

#### Step D5: Confirmation and writing with markers

If the plan suits you — reply `OK, apply`. A4 writes `draft/SRS-v<N+1>.md`, where **every new or changed line carries a marker**:
- `*(new: <source>)*` — a new section/requirement/table row;
- `*(changed: <reason>)*` — a change to an existing baseline.

The absence of a marker = a declaration that "the baseline is preserved here 1:1".

#### Step D6: Recording and validation

```bash
uv run cli.py draft --project=my-app --doc=SRS    # → status: validating
# Next — the standard validation (RMVAL) and finalization cycle (Steps B4–B5)
```

> 📖 **A full walkthrough on the real DAMS case** — with the Δ1–Δ7 delta, a sample diff plan, and a table of protection mechanisms: [`docs/walkthroughs/augment-dams-srs.md`](walkthroughs/augment-dams-srs.md).

---

## 4. Integration with Obsidian and NotebookLM

### Obsidian (visual knowledge base)
1. Install [Obsidian](https://obsidian.md/).
2. Open the `vault/` folder of your project as a vault (Obsidian Vault).
3. Run the sync in the terminal:
   ```bash
   uv run cli.py sync-vault
   ```
4. You get an interactive graph of specification links, tags, and cross-references for convenient reading.

### Google NotebookLM (smart RAG search and audio podcasts)
1. Prepare the project export:
   ```bash
   uv run cli.py export-notebooklm --project=my-app
   ```
2. Open [Google NotebookLM](https://notebooklm.google/).
3. Create a new notebook and upload the generated files from the `notebooklm/my-app/` folder there.
4. Ask the AI any questions about the project, generate summaries or audio podcasts!

---

## 5. Automatic Requirements Mind update (one-click Update)

To update the tool to the latest version from GitHub, you do not need to delete the project or reinstall files by hand. Just run a single command in the terminal:

```bash
uv run cli.py update
```

**What the update process does:**
1. **Updating the core files:**
   * If the project is a Git repository — `git pull origin main` is run automatically.
   * If the project was installed from a ZIP archive — the script downloads a fresh ZIP distribution from GitHub and carefully updates all the core files (the client, the documentation, the `flows/` scripts, and the `kb/` knowledge base), while your project folders (`projects/`), customizations, and the `.env` settings file remain completely safe.
2. **Updating dependencies:** new libraries from `requirements.txt` are checked and reinstalled (using `uv` or standard `pip`).
3. **Updating the IDE AI skills:** the script automatically runs `setup-ide` to copy the new AI skills, instructions, and `.cursorrules` rules into all your AI assistants (Cursor, Claude Code, Google Antigravity, OpenAI Codex).

---

## 6. Running via the OpenAI Codex CLI

The Codex CLI (OpenAI Codex) works through terminal directives:

```bash
# Initialize the project
codex --model=gpt-4o --prompt="Run the Requirements Mind installation"

# Start onboarding
codex --model=gpt-4o --prompt="@AGENTS.md @.cursorrules
Run RMONB for the project <name>"

# Start Intake
codex --model=gpt-4o --prompt="@AGENTS.md @.cursorrules
Run RMIN for the project <name>"

# Start Elicitation Mode
codex --model=gpt-4o --prompt="@AGENTS.md @.cursorrules
Run RME for the new project <name>"

# Start Draft
codex --model=gpt-4o --prompt="@AGENTS.md @.cursorrules
Run RMDW for the project <name>, I need an SRS"

# Start Validation
codex --model=gpt-4o --prompt="@AGENTS.md @.cursorrules
Run RMVAL for the project <name>"
```

**Important:** In the Codex CLI you must explicitly include `@AGENTS.md` and `@.cursorrules` in the prompt, so the agent sees the context of the agent Rules and the Capabilities Menu.
