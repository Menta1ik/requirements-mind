# Flow: 01-intake (Initial requirements gathering)

This flow describes the process of parsing the raw inputs from the `input/` folder and building the project's initial context.

## 👥 Roles involved
* **A1 — Intake Analyst**

## 🏁 Inputs
* Files in the `projects/<project-name>/input/` folder (for example, `transcript.md`, `requirements.md`).

## ⚙️ Step-by-step process

1. **Launch the command:**
   The user or a script invokes:
   ```bash
   uv run cli.py intake --project=<name>
   ```
2. **Analyze the inputs:**
   Agent A1 scans all files in `input/`, indexes their content, removes noise, and classifies the requirements.
3. **Assess sufficiency:**
   - If the source text is enough to extract a Vision and at least three functional requirements → proceed to step 4.
   - If the files are empty or contain incoherent noise → A1 sets the status `needs_questions` in `state.json` and aborts the flow.
4. **Create context.md:**
   A1 generates the file `projects/<project-name>/context.md` with strict traceability to the source files.
5. **Update the state:**
   The AI orchestrator moves `state.json` to status `drafting` (or `needs_questions` when data is insufficient).
