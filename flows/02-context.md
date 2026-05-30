# Flow: 02-context (Maintaining the project context)

This flow describes the rules for maintaining and updating the `context.md` file as the single source of truth.

## 👥 Roles involved
* **A1 — Intake Analyst**
* **Master Orchestrator**

## 🏁 Inputs
* The existing `projects/<project-name>/context.md`
* New user answers from `qa-history.md` (if present)

## ⚙️ Step-by-step process

1. **Launch the update:**
   When new data arrives from the user, the context-enrichment process starts.
2. **Integrate the answers:**
   Agent A1 matches the questions from `questions.md` against the user's answers in `qa-history.md`.
3. **Update context.md:**
   A1 integrates the new facts into the corresponding sections of `context.md` (for example, extends the technology-stack requirements or the functionality), preserving backward compatibility.
4. **Clean up the questions:**
   Agent A1 removes the answered questions from `questions.md` and resets the `open_questions` field in `state.json`.
5. **Record the version:**
   The `last_updated` field is updated in `state.json`. The context is ready for the draft-development stage (`drafting`).
