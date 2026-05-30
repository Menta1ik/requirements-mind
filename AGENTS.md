# The Requirements Mind multi-agent team

The **Requirements Mind** project uses a decentralized AI team of agents built on the **BMAD METHOD**. Each agent is a narrowly specialized expert in its own area, fully focused on requirements engineering and systems analysis.

---

## 👥 Agent roles and specialization

### 0. 🧭 A0 — Onboarding Wizard (AI project-start assistant)
* **Purpose:** The analyst's first meeting, running Project Discovery, helping to choose one of the **6 target requirements profiles**, and building a personal project Roadmap. Directs the user toward gathering requirements from scratch or parsing raw inputs.

### 1. 👑 Master Orchestrator
* **Based on:** BMAD `bmad-party-mode`
* **Purpose:** Coordinating the round table, managing sessions and state transitions in `state.json`. Analyzes the Validator's reports and decides whether artifacts are ready, automatically launching specification finalization in the CLI.

### 2. 📊 A1 — Intake Analyst
* **Based on:** BMAD `bmad-agent-analyst` + `bmad-index-docs`
* **Purpose:** Parsing raw text files and transcripts in the `input/` folder, removing conversational noise, extracting the key facts, and building a single detailed project context (`context.md`) with a strict ban on data compression (No Compression).

### 3. 📋 A3 — Question Generator & Elicitation Expert (requirements interviewer)
* **Based on:** BMAD `bmad-agent-pm` + `bmad-advanced-elicitation`
* **Purpose:**
  * In **Elicitation Mode (Profile 6)** it runs a deep interactive interview from scratch using the hybrid **"Pragmatic Analyst"** standard (JTBD + Use Cases + ISO 29148 NFR) and creates `requirements.md` itself.
  * In **gap-clarification mode** it surfaces inconsistencies in `context.md`, prints up to 5 targeted questions right into the IDE chat with a mandatory free-input option, writes the results into `qa-history.md`, and moves the project forward.

### 4. 💻 A4 — Document Writer
* **Based on:** BMAD `bmad-agent-tech-writer` + `bmad-create-prd` + `bmad-edit-prd` + `bmad-spec`
* **Purpose:** Writing formal specifications (BRD, SRS, Tech Design, API Contract) strictly per the `kb/` knowledge-base checklists and based on the user's answers.
* **Two modes via the `rm_mode` field in `context.md`:** `draft` (writing from scratch per the checklist) and `augment` (protected extension of a baseline document — see the "🛡️ Augment Mode" section below).

### 5. 🏗️ A2 — Requirements Validator
* **Based on:** BMAD `bmad-validate-prd` + `bmad-review-adversarial-general` + `bmad-review-edge-case-hunter`
* **Purpose:** Rigorous quality control of drafts. Hunts for logical inconsistencies, edge cases, and missed details. Issues `PASSED`/`FAILED` verdicts.

### 🔍 6. A5 — Research Assistant (technical researcher)
* **Based on:** BMAD `research` + `bmad-brainstorming`
* **Purpose:** Analyzing external industry standards and best practices on request from a developer or architect.

### 📈 7. A6 — Analysis Writer
* **Purpose:** Flexible analysis (Mode B). Not tied to rigid formats; designs the report structure itself (version-comparison tables, risk lists) in the `analysis/` folder.

---

## 🧭 Principles of agent interaction

1. **A single context (`context.md`):** All agents write and cross-check their conclusions based only on the single project context. No designing "out of thin air".
2. **Versioning:** Any change to a draft produces a new file version (v1, v2, v3...). Old versions are never overwritten, to preserve history in Git.
3. **Strict traceability:** Every technical requirement in an SRS or Tech Design must reference the corresponding business requirement in the BRD.
4. **CLI command automation:** Once their work is done (writing a requirements file, a context, a draft, or a report), the AI agents **propose and run the needed CLI command on their own** in the IDE terminal (`onboard`, `intake`, `draft`, `validate`, `final`). The user does not need to keep the commands in mind — they just confirm the run in the IDE chat.
5. **Seamless interactive Q&A right in the IDE chat:** Any clarifying questions are printed by agent A3 right into the chat with ready-made answer options.
6. **Mandatory free-text answer:** Every dynamic question from the A3 AI interviewer always includes a final free-input item (for example: *"Your own option / Free-text answer"*), so the analyst can describe requirements in their own words. The AI carefully records and appends the answers into `qa-history.md`.
7. **The working mode is set in `context.md` (`rm_mode`):** All agents must read the `rm_mode` field in the `context.md` frontmatter and not slide into the default mode when a baseline is present. `draft` — building from scratch; `augment` — protected extension of an existing document (see the "🛡️ Augment Mode" section).

---

## 🛡️ Augment Mode (extending a baseline without rebuilding)

When the analyst already has a formal document (SRS/BRD/Tech Design/API Contract) and needs to **extend** it with artifacts (transcripts, new BRs, notes) rather than rebuild it from scratch, the team works in `rm_mode: augment`. The baseline remains "the law"; edits are made only surgically and only with the user's explicit consent. The full flow is `flows/09-augment.md`.

The augment-mode contract is distributed across the agents as follows:

* **A1 — Intake Analyst** distinguishes baseline vs artifacts: it identifies the baseline document, sets `rm_mode: augment` and the mandatory `baseline_doc` field in the `context.md` frontmatter, and records only the **delta** in `context.md` (what new content came from the artifacts), without dissolving the baseline into the general context.
* **A4 — Document Writer** works in protected mode: it preserves the baseline's structure and wording, presents a **diff plan** of the edits before writing and waits for the user's explicit confirmation, and overrides the "deep detailing" principle (vague spots in the baseline go into "❓ Open questions and gaps" rather than being filled in out of thin air). The result is saved as `draft/<doc>-v<N+1>.md`. Details — the "Augment Mode" block in `skills/rm/a4-document-writer.md`.
* **A2 — Requirements Validator** in augment mode checks exactly the delta and the preservation of the baseline (it does not penalize inherited wording for being "under-detailed"), relying on the soft `kb/` checklists.
* **Master Orchestrator** enforces the contract: it blocks the implicit slide into `draft` when a `baseline_doc` is present, and does not allow writing without a confirmed diff plan.

> **A6 — Analysis Writer is deliberately outside the contract.** A6 writes into a separate `analysis/` folder and never edits the baseline, so it does not need the augment-mode protection — it stays flexible (Mode B).

---

## 💻 Usage examples in AI tools

Since the AI skills are integrated into your development environment (Cursor, Claude Code, Antigravity, OpenAI Codex), you can invoke the agents using short **command codes (Capabilities Menu)** in the IDE chat or via console directives:

### 1. Start gathering requirements from scratch (Elicitation Mode)
In the AI assistant's chat (for example, Mary) write:
> **"Hi! Run RME for the new project my-app"**
*The AI will run a deep interview based on JTBD, Use Cases, and ISO 29148, write `requirements.md` and `context.md` itself, and then automatically propose running the onboard command in the terminal (the user just confirms the run in the chat).*

### 2. Start onboarding (Project Discovery)
In the AI assistant's chat write:
> **"RMONB for the project my-app"**
*Agent A0 will run the survey across the 6 requirements profiles, build a personal Roadmap, and automatically propose running the onboard command in the terminal (with confirmation in the chat).*

### 3. Start Intake analysis of raw files
In the AI assistant's chat write:
> **"RMIN for the project my-app"**
*Agent A1 will analyze the incoming `input/` folder, create `context.md`, and automatically propose running the command `uv run cli.py intake` (with confirmation in the chat).*

### 4. Start generating a specification draft
In the AI assistant's chat (for example, John) write:
> **"John, run RMDW for the project my-app. I need an SRS draft"**
*Agent A4 will generate the specification per the `kb/` standards and automatically propose running the command `uv run cli.py draft` (with confirmation in the chat).*

### 5. Start checking a draft
In the AI assistant's chat write:
> **"RMVAL for the project my-app"**
*Agent A2 will check the document, write a detailed report into `messages/` with a `PASSED`/`FAILED` verdict, and automatically propose running the command `uv run cli.py validate` (with confirmation in the chat).*

### 6. Tier 1 — deterministic ID check (no LLM)
Before running `RMVAL` (Tier 2, LLM) it is recommended to run the cheap regex linter, which catches duplicate IDs, orphan references, and uncovered Business Goals in milliseconds:
```bash
uv run cli.py trace --project=my-app
# or a single document:
uv run cli.py trace --project=my-app --doc=SRS --version=1
```
Exit codes: `0` — clean, `1` — there are traceability errors, `2` — invocation error. **If the agent sees that a draft has just been written, it should itself propose that the user run `trace` before `validate` — this saves A2's context.** The command does not modify `state.json` — it is a pure form check.
