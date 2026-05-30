# Flow: 09-augment (Extending an existing document with artifacts)

This flow describes the case where the analyst already has a formal document (SRS, BRD, Tech Design, API Contract) and needs to **extend** it based on new artifacts (meeting transcripts, updated BRs, notes), **while preserving the existing structure and wording**.

This is an alternative to `04-draft` (writing from scratch) and `07-analyze` (a standalone analytical report). The key difference: the baseline document remains "the law", and A4 (Document Writer) works in protected augment mode with a mandatory diff plan and explicit user confirmation before writing.

## 👥 Roles involved

* **A1 — Intake Analyst** (distinguishes baseline vs artifacts, sets `rm_mode: augment` in `context.md`)
* **A4 — Document Writer** (works in protected augment mode — see the "Augment Mode" block in `skills/rm/a4-document-writer.md`)
* **Master Orchestrator** (enforces the augment contract)

## 🏁 Inputs

* The baseline document — an existing SRS/BRD/Tech-Design/API-Contract (`.md`, `.docx`, `.pdf`).
* Artifacts for enrichment — meeting transcripts, new requirements, notes in any textual format.

## ⚙️ Step-by-step process

1. **Launch augment mode:**
   The user runs the command:
   ```bash
   uv run cli.py augment --project=<name> --baseline=<path-to-baseline> --doc=SRS
   ```
   The command:
   - copies the baseline into `projects/<name>/input/baseline/`,
   - creates/updates `context.md` with frontmatter:
     ```yaml
     rm_mode: augment
     baseline_doc:
       path: input/baseline/<name>
       type: SRS
       preserve_structure: true
     ```
   - moves `state.json` to `status: drafting`, `mode: augment`,
   - prints instructions for the AI assistant to run A1 → A4.

2. **Intake under augment (A1):**
   The analyst asks the AI to run `a1-intake-analyst`. A1:
   - reads all artifacts from `input/` (except `input/baseline/`),
   - **does not dissolve the baseline into `context.md`** — it keeps a reference via `baseline_doc.path`,
   - builds a **"🔄 Delta to extend the baseline"** section in `context.md` with a list of "which new facts came from the artifacts and where to embed them in the baseline",
   - sets `rm_status: complete` or `incomplete` according to the usual rules.

3. **Diff plan and confirmation (A4):**
   After `cli.py intake`, the analyst asks the AI to run `a4-document-writer`. In augment mode, A4:
   - reads the baseline in full and reads the delta from `context.md`,
   - **prints a diff plan in the chat**: what new content it will add, what it will change in the existing sections (with justification and a reference to the artifact), which sections it will keep 1:1,
   - **waits for the user's explicit confirmation** (`OK`, "apply", etc.),
   - only after confirmation writes `draft/<doc>-v<N+1>.md` with the markers `*(new: …)*` / `*(changed: reason)*` in the headings and lines themselves.

4. **Record the draft:**
   After the file is written — the standard command:
   ```bash
   uv run cli.py draft --project=<name> --doc=<SRS/BRD/...>
   ```
   Moves the project to `status: validating`.

5. **Validation (A2) — soft mode:**
   A2 reads `rm_mode: augment` from `context.md` and applies the augment policy to `kb/<doc>-checklist.md`: `required` items block (FAIL), `optional-augment` items go into a separate "⚠️ Augment-soft" block of the report as warnings without blocking the verdict. Additionally, A2 checks the augment contract: baseline sections renamed/removed without the `*(changed: reason)*` marker → Blocker.

6. **Finalization:**
   ```bash
   uv run cli.py final --project=<name> --doc=<doc> --version=<N+1>
   ```

## 🛡️ The baseline-protection contract

The contract is nailed down in three places at once:
- `skills/rm/a1-intake-analyst.md` — A1 sets `rm_mode: augment` in the frontmatter.
- `skills/rm/a4-document-writer.md` — in augment mode A4 forbids rebuilding the structure and requires markers and a diff plan.
- `skills/rm/master-orchestrator.md` — the orchestrator returns the document to `needs_revision` if A4 broke the contract (no diff plan / no markers).

## 📋 When NOT to use augment

- If the baseline document is outdated or structurally incorrect and you deliberately need to rewrite it — use `04-draft` (from scratch).
- If the task is a standalone analytical report (risks, comparisons, contradictions) and the baseline should not be touched at all — use `07-analyze`.
- If you need a cross-agent discussion of a contested decision — use `08-collaborate`, then `09-augment` to apply the decision.
