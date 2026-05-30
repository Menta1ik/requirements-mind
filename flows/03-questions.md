# Flow: 03-questions (Requirements interviewing)

This flow describes the process of surfacing gaps and generating clarifying questions for the user.

## 👥 Roles involved
* **A3 — Question Generator**
* **Master Orchestrator**

## 🏁 Inputs
* Recorded gaps in `projects/<project-name>/context.md`.

## ⚙️ Step-by-step process

1. **Activation trigger:**
   Activated automatically when the status in `state.json` is `needs_questions`.
2. **Analyze the gaps:**
   Agent A3 reads the gaps in `context.md` and forms a list of **no more than 5 targeted questions**.
3. **Write to questions.md:**
   A3 writes the questions into the file `projects/<project-name>/questions.md` with answer options and a description of their impact on the architecture.
4. **Interactive interview in the IDE chat (RMQ):**
   The A3 AI agent automatically prints the questions right in the IDE chat with ready-made answer options and a mandatory free-input option.
5. **Save the answers:**
   The user's answers are written into `projects/<project-name>/qa-history.md`, and the project status in `state.json` is moved back to `drafting` (the AI automatically reruns Intake to update `context.md`).
