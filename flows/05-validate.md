# Flow: 05-validate (Validation of the produced documents)

This flow describes the process of automatic and cross-agent document quality control.

## 👥 Roles involved
* **A2 — Requirements Validator**
* **Master Orchestrator**

## 🏁 Inputs
* A draft document (for example, `projects/<project-name>/draft/BRD-v1.md`).

## ⚙️ Step-by-step process

1. **Launching validation (RMVAL):**
   The AI agent automatically proposes running the validation command in the terminal once the draft stage is complete:
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py validate --project=<name> --doc=BRD --version=1
   ```
2. **Boundary-condition checks:**
   Agent A2 inspects the draft for compliance with the `kb/` checklists and writes the critical findings into `messages/a2-to-a4-vN.md`.
3. **Orchestrator assessment:**
   The Master Orchestrator reads A2's report:
   - If the report contains a `FAILED` status or critical findings (Blockers) → the orchestrator changes the project status in `state.json` to `needs_revision` and triggers another iteration (runs the `04-draft` flow for version vN+1).
   - If the report passed successfully (status `PASSED`) → the orchestrator changes the project status to `approved`.
