# Flow: 00 — Requirements project onboarding and Project Discovery

This flow describes the very first step of a systems analyst's work in Requirements Mind — creating a project and running the initial onboarding interview with the **Onboarding Wizard (A0)** AI agent.

---

## 🌟 Step 1: Initialize the project in the CLI
The analyst creates a new project workspace in the terminal:

```bash
uv run cli.py init --project=my-new-app
```

**What happens:**
* The CLI creates the directory structure under `projects/my-new-app/`.
* A starter state file `state.json` is created with status `onboarding`.
* The terminal prints a nice prompt to launch the Onboarding Wizard (A0).

---

## 💬 Step 2: Initial interview with the Onboarding Wizard (A0)
1. The analyst opens a chat with their AI assistant in the IDE or CLI (Cursor, Claude Code, Antigravity, OpenAI Codex) and enters the command:
   > **"Mary, let's run onboarding (RMONB) for the new project my-new-app"**
2. **The A0 AI agent enters the dialogue:**
   * It interviews the analyst step by step to determine one of the **6 target requirements-project profiles**:
     1. **Profile 1: "Business concept"** (goal: conceptual business requirements **BRD**).
     2. **Profile 2: "System specification"** (goal: detailed requirements and system logic **BRD ➡️ SRS**).
     3. **Profile 3: "Architecture design"** (goal: architectural flows and the database structure **BRD ➡️ SRS ➡️ Tech Design**).
     4. **Profile 4: "Integration and API"** (goal: the full design cycle, including REST/gRPC contracts **BRD ➡️ SRS ➡️ Tech Design ➡️ API Contract**).
     5. **Profile 5: "Analytical research (Mode B)"** (goal: free-form requirements analysis, document comparisons, risk and contradiction matrices in the **`analysis/`** folder).
     6. **Profile 6: "Requirements elicitation" (Elicitation Mode)** (goal: gathering requirements from scratch through an AI interview in the chat, when the analyst has only an idea).
   * The AI agent records the chosen profile in `state.json` (for example, `"profile": 6`).

---

## 🧭 Step 3: Branching the onboarding logic

### Option A: Profile 1–5 chosen (raw inputs exist)
1. The analyst states which documents they already have (transcripts, specs, ticket lists).
2. The Onboarding Wizard gives clear instructions on which files of the `input/` folder to copy them into:
   * `input/requirements.md` — textual requirements.
   * `input/transcript.md` — meeting transcripts.
3. The AI agent builds a starter `context.md` file with references to the inputs.

### Option B: Profile 6 chosen (requirements from scratch / Elicitation Mode)
1. The system automatically activates the custom skill **`a3-elicitation`**.
2. The AI interviewer conducts a deep survey using the hybrid **"Pragmatic Analyst"** methodology (JTBD + Use Cases + ISO 29148 NFR).
3. At the end of the dialogue the AI generates and saves the files `input/requirements.md` and `context.md` to disk on its own.
*(A detailed description of the process is given in the flow [flows/09-elicitation.md](file:///Users/macbook/Projects/requirements-mind/flows/09-elicitation.md))*

---

## 🏁 Step 4: Record onboarding completion in the CLI
Once the starter `context.md` skeleton has been created (manually by the analyst or automatically by the `a3-elicitation` AI agent), the analyst runs the command in the terminal:

```bash
uv run cli.py onboard --project=my-new-app
```

**What happens:**
* The CLI checks that the created files are present on disk.
* It prints a nice welcome message and a cheat sheet for the next stage.
* It moves the project status in `state.json` from `onboarding` to **`intake`** (the project is ready for a deep requirements analysis by the `a1-intake-analyst` AI agent).
