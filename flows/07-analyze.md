# Flow: 07-analyze (General requirements analysis in Mode B)

This flow describes the process of launching a free-form, flexible analytical investigation.

## 👥 Roles involved
* **A6 — Analysis Writer**
* **A5 — Research Assistant** (on request)

## 🏁 Inputs
* Any project documents (inputs, drafts, final versions).
* The text of the analytical task from the user.

## ⚙️ Step-by-step process

1. **Launch the analysis:**
   The user runs the command:
   ```bash
   uv run cli.py analyze --project=<name> --task="Find the risks of integrating with the CRM"
   ```
2. **Analyze the context:**
   Agent A6 reads the project files, matches them against the stated task, and starts the investigation.
3. **Produce the report:**
   A6 designs the optimal report structure on its own (matrices, comparison tables, risk lists) and writes the results to `projects/<project-name>/analysis/analysis-vN.md`.
4. **Update the state:**
   The orchestrator records the completion of the analytical session in `state.json` and notifies the user that the report is ready.
5. **Obsidian sync:**
   The result becomes available for viewing and navigation in the Obsidian Vault.
