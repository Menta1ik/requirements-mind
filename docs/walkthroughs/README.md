# Walkthroughs — detailed work scenarios

This folder holds the **working walkthroughs** of Requirements Mind: step-by-step breakdowns of real cases with concrete prompts for the AI assistant, CLI commands, expected artifacts, and typical mistakes.

They complement:
- `docs/user-guide.md` — the general user guide,
- `docs/specification_v2.md` — the formal architecture specification,
- `flows/0X-*.md` — the formal flow descriptions (what each step does),
- `skills/rm/a*.md` — the agent instructions (exactly how an agent should behave).

Walkthroughs are needed where the formal description is not enough — when the team needs to see **"this is what it looks like in real work on real artifacts"**.

## 📚 Available walkthroughs

| File | Scenario | On which case |
|---|---|---|
| [`augment-dams-srs.md`](augment-dams-srs.md) | `09-augment` — extending an existing SRS with artifacts | DAMS (Document Asset Management Service): SRS-v1 + a meeting transcript from 26.06 → SRS-v2 with the markers `*(new)*` / `*(changed)*` |

## 🗺️ Roadmap

Detailed walkthroughs like this are planned for **all modes** of Requirements Mind. Priority is by usage frequency and the risk of mistakes without them:

| Scenario | File (planned) | When it is needed | Status |
|---|---|---|---|
| `09-augment` | `augment-dams-srs.md` | Extending an existing document with artifacts without rebuilding the structure. **High risk of "made-up content" if done without guardrails.** | ✅ Ready |
| `04-draft` | `draft-greenfield-srs.md` | Writing an SRS/BRD from scratch per the checklist. The basic scenario, but the team needs a reference example of "what a good context.md → BRD-v1 → SRS-v1 should look like". | ⏳ Planned |
| `01-intake` | `intake-noisy-inputs.md` | When "dirt" arrives in `input/` (mixed-format files, contradictions, incompleteness). How A1 correctly records conflicts in `## ⚠️ Detected requirement conflicts`. | ⏳ Planned |
| `05-validate` + `06-final` | `validation-and-finalize.md` | The A4 ↔ A2 validation cycle with findings, the transition to `final/`. How to read `messages/a2-to-a4-vN.md` and not get stuck in iterations. | ⏳ Planned |
| `07-analyze` | `analyze-risk-matrix.md` | A free-form analytical report (Mode B): risks, contradictions, comparisons. When to choose analyze, and when — augment. | ⏳ Planned |
| `08-collaborate` | `collaborate-conflicting-decision.md` | Party Mode on a contested decision. How to read `orchestrator-decision.md` and not get "weighted-average garbage". | ⏳ Planned |
| `03-questions` | `questions-from-incomplete.md` | A3 generates clarifying questions from `## ❓ Open questions and gaps`. How to phrase answers so that A1 embeds them correctly into `context.md`. | ⏳ Planned |

## 🧱 Walkthrough structure (template)

Each walkthrough should contain:

1. **Context** — what the analyst had as input, what they wanted, what came out / could have gone wrong.
2. **Steps** — concrete CLI commands and prompts for the AI assistant in the IDE. Not "run A4", but the **verbatim prompt text**.
3. **Expected artifacts** — what should be in `context.md`, `draft/`, `messages/` after each step. With real text fragments.
4. **Protection mechanisms** — a table of "which guardrail would fire on a typical mistake in this scenario".
5. **Rules for the team** — a short checklist of the rules that must not be broken in this mode.

This structure is the same for all walkthroughs — the team knows where to look for what.

## 🤝 How to add a walkthrough

1. Take a real case from your work (or a recorded bug report from an analyst).
2. Fill in the template above.
3. Put it in this folder with the name `<scenario>-<short-case>.md` (for example, `draft-payments-brd.md`).
4. Add a row to the "Available walkthroughs" table.
5. If the walkthrough uncovered a new class of mistakes — open a task to fix the corresponding skill or flow.
