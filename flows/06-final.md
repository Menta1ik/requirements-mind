# Flow: 06-final (Finalizing the documents)

This flow describes the process of finalizing approved drafts and moving them to their final status.

## 👥 Roles involved
* **Master Orchestrator**

## 🏁 Inputs
* An approved specification draft (for example, `projects/<project-name>/draft/BRD-v2.md`).
* Status `approved` in `state.json`.

## ⚙️ Step-by-step process

1. **Launch finalization:**
   The AI agent automatically proposes running the finalization command in your terminal:
   ```bash
   # RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
   uv run cli.py final --project=<name> --doc=BRD --version=2
   ```
   *(You just press the confirm-run button in the chat.)*
2. **Move the document:**
   The orchestrator copies the approved draft version `draft/BRD-v2.md` into the final-versions folder `final/BRD-v2-final.md`.
3. **Update the registry:**
   Information about the successful finalization is recorded in `metadata.json`, including the date and the version hash.
4. **Produce the decision report:**
   The orchestrator generates `messages/orchestrator-decision.md` with a summary of the work done.
5. **Readiness for the next stage:**
   The project is moved to a neutral state, ready to start generating the next document in the hierarchy (for example, an SRS based on the finalized BRD).
