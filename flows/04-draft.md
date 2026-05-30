# Flow: 04-draft (Drafting the documents)

This flow describes the process of writing specifications (Mode A) against rigid checklists.

## 👥 Roles involved
* **A4 — Document Writer**
* **A5 — Research Assistant** (on request)

## 🏁 Inputs
* `projects/<project-name>/context.md`
* Checklists from `kb/` (for example, `kb/srs-checklist.md`).

## ⚙️ Step-by-step process

1. **Launch generation:**
   The user runs the command:
   ```bash
   uv run cli.py draft --project=<name> --doc=BRD
   ```
2. **Check the checklist requirements:**
   A4 loads the corresponding checklist from `kb/` and starts writing the specification sections.
3. **Research request (optional):**
   If needed, A4 can invoke A5 to clarify security standards or design patterns.
4. **Write the draft:**
   A4 generates the file `projects/<project-name>/draft/BRD-vN.md` (where `N` is the current iteration number).
5. **Update the state:**
   The AI orchestrator increments the iteration number and moves the project status to `validating`.
