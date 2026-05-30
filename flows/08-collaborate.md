# Flow: 08-collaborate (Cross-agent round table / Party Mode)

This flow describes the process of launching a collaborative requirements discussion by a group of AI agents.

## 👥 Roles involved
* **Master Orchestrator**
* A set of selected agents (for example, **A1, A2, A4**)

## 🏁 Inputs
* The current project status in `state.json`.
* A topic or problem to discuss.

## ⚙️ Step-by-step process

1. **Launch the round table:**
   The user runs the command:
   ```bash
   uv run cli.py collaborate --project=<name> --agents="a2,a4"
   ```
2. **Initialize the session:**
   The orchestrator prepares the round-table context, gathers the latest document versions, and distributes the system prompts to the selected agents.
3. **Exchange messages:**
   - The Validator (A2) generates its objections and critique.
   - The Writer (A4) reacts to the critique, describing the planned changes.
   - All messages are saved into the cross-agent letter files in `projects/<project-name>/messages/`.
4. **Orchestrator summary:**
   The orchestrator analyzes the discussion and produces `orchestrator-decision.md` with the final decisions and an action plan.
5. **Record the results:**
   The active agents and the current status are updated in `state.json`, and the project is moved to the draft-revision stage.
