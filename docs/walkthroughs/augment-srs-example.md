# Augment walkthrough: extending an existing SRS

This document is a worked example of how the case "extend the SRS based on a
clarification meeting" should go, and how `augment` mode differs from `draft`.
It uses a fictional **File Storage Service (FSS)** as the subject so the
mechanics stay clear without depending on any real project.

## 📌 Context

**What the analyst had:**
- `SRS-v1.md` — a formal SRS for FSS (a hypothetical file storage service) with a
  detailed structure: 11 sections, a data model in tabular form, a validation
  matrix, key parameters.
- `meeting-notes.txt` — a transcript of a discussion with the team: clarifications
  on async file processing, profile statuses, the content-hash format, and
  duplicate behavior.
- `srs-skeleton.txt` — a bare SRS skeleton (headings only, no tables).

**What the analyst wanted:**
> "Extend the existing SRS with the clarifications from the meeting. Don't touch the structure — it's agreed upon."

**What they got (the failure mode this example prevents):**
The AI rewrote the "6. Data Model" section into a new "7.1 Data Entities + 7.2 Data Dictionary" structure, merged two attribute tables into a single `USER_PROFILE` entity, duplicated `content_hash` in `USER_PROFILE` and in a new `FILE` entity, and renamed `file_ref` → `file_id` — without any agreement. The whole profile section came back as invented content the analyst never asked for.

## 🔍 How to run this case correctly through Requirements Mind v2.1

### Step 1. Launch the augment command

```bash
uv run cli.py init --project=fss-srs-augment
uv run cli.py augment \
  --project=fss-srs-augment \
  --baseline=path/to/SRS-v1.md \
  --doc=SRS
```

The command:
- places `SRS-v1.md` into `projects/fss-srs-augment/input/baseline/`,
- creates `context.md` with the frontmatter:
  ```yaml
  rm_mode: augment
  baseline_doc:
    path: input/baseline/SRS-v1.md
    type: SRS
    preserve_structure: true
  ```
- moves the project to `status: drafting, mode: augment, active_agents: [a1]`.

Next the analyst places `meeting-notes.txt` into `projects/fss-srs-augment/input/` (alongside the `baseline/` subfolder, **not inside it**).

### Step 2. A1 parses the artifacts into a delta (not into the full context.md)

Prompt for the AI assistant in the IDE:
> "Run `a1-intake-analyst` for the project `fss-srs-augment`. This is augment mode, the baseline is `input/baseline/SRS-v1.md`. Do not dissolve the baseline into `context.md`. In the '🔄 Delta to extend the baseline' section describe only the new facts from `meeting-notes.txt` and where to embed them in the baseline."

A1 writes roughly the following into `context.md`:

```markdown
## 🔄 Delta to extend the baseline

### New requirements from meeting-notes.txt

| # | Fact from the meeting | Where in the baseline | Edit type |
|---|---|---|---|
| Δ1 | Async file processing: after the initial validation (hash, size, extension) — `202 Accepted`, antivirus and the binding to the profile happen asynchronously | § 3.2 "File upload" — add FR-UPL-2 | new FR |
| Δ2 | Async-processing status: the client must have a way to find out when the file is actually bound | § 3.2 — add FR-UPL-3; § 4 — add UC-UPL-STATUS | new FR + new UC |
| Δ3 | Downloading a file via a pre-signed/temporary link — a separate step, not described in the baseline | § 4 — add UC-DWL-2 | new UC |
| Δ4 | The initiating client is recorded as part of the profile data, not only in the log | § 6 "Data model", table 13 — clarify the role of CreatorID (was mandatory, stays; add the note "used for audit and file attribution") | clarification |
| Δ5 | The temporary-link TTL → an explicit value is needed (in the baseline `NFR-SEC-02` has no number) | § 4.4 "Security", NFR-SEC-02 | open question — the team did not name a concrete TTL value |
| Δ6 | Antivirus → async, NSFW check → disabled in the first iteration | § 8 "Configurable parameters", table 16 — already reflected in the baseline; reconcile with § 3.2 | clarification of the existing |
| Δ7 | On the hash: "SHA-256?" in the baseline → confirmed as SHA-256 | § 9, table 17 + § 7, table 15 (VAL-03) | clarification of the existing |

### What was NOT discussed in the meeting (stays as in the baseline)

- § 1 "Introduction", § 2.1-2.5 "Overview" — were not revisited.
- § 4.1 NFR-AVL-01 (uptime 99.9%) — was not revisited.
- § 7 "Validation matrix" VAL-01, VAL-02, VAL-04..09 — were not revisited.
- The structure of "6. Data model" (two tables: file attributes + profile attributes) — was NOT revisited. The team did not ask to merge the entities.

## ❓ Open questions and gaps

- OQ-01: The concrete temporary-link TTL value (`download_link_ttl`) — the team did not name a number.
- OQ-02: The CreatorID format — UUID, string, something else? [Δ4]
- OQ-03: Is the content hash specifically a 64-character SHA-256 hex string? The meeting confirmed "SHA-256", but the regex format was not stated explicitly. [Δ7]
```

In the frontmatter A1 sets `rm_status: incomplete` — we have OQ-01/02/03.

### Step 3. A3 asks clarifying questions (optional)

```bash
uv run cli.py intake --project=fss-srs-augment
```

Since `rm_status: incomplete`, the project goes to `needs_questions`. The analyst runs `a3-question-generator`, gets three questions on OQ-01/02/03, answers them or marks "leave as ⚠️ TBD in the document". After that — updates `context.md` → `rm_status: complete` → runs `cli.py intake` again → `drafting`.

### Step 4. A4 writes the diff plan into the chat — **BEFORE** writing the file

Prompt:
> "Run `a4-document-writer` for the project `fss-srs-augment`. This is augment mode. Show me the diff plan and wait for my confirmation before writing `draft/SRS-v2.md`."

A4 (correct behavior) prints into the chat:

```
📋 Plan to extend input/baseline/SRS-v1.md (rm_mode: augment)
════════════════════════════════════════════════════════════════

➕ New (from the artifacts):

  § 3.2 FR-UPL-2 "Async file intake with a security queue" *(new)*
    Source: meeting-notes.txt (Δ1)
    Text: "The system shall synchronously accept the file, run validation
    against the matrix (VAL-01..03, VAL-06, VAL-08), enqueue an async
    security check, and return HTTP 202 Accepted to the client. The actual
    persistence to storage and the binding to the profile happen after a
    successful async processing pass."

  § 3.2 FR-UPL-3 "Async-processing status of a file" *(new)*
    Source: Δ2

  § 4 UC-UPL-STATUS "Retrieving the async-processing status of a file" *(new)*
    Source: Δ2

  § 4 UC-DWL-2 "Downloading a file via a temporary link" *(new)*
    Source: Δ3

✏️ Changed in the baseline:

  § 7 validation matrix, VAL-03 "Hash": clarify the regexp `^[a-f0-9]{64}$`
    *(changed: SHA-256? → SHA-256 confirmed, source Δ7)*

  § 9 key parameters, table 17: remove the "?" from "SHA-256?"
    *(changed: formal confirmation from the meeting, Δ7)*

  § 6 data model, table 14 "Profile states":
    add that the transition Created → File_Linked happens after a successful
    async processing (and not immediately after UC-UPL-1).
    *(changed: clarification of the transition moment, Δ1)*

  § 4.5 NFR-AUD-01: add "CreatorID is stored in the profile and is used
    for auditing".
    *(changed: clarification from Δ4)*

⛔ NOT touching (the baseline is preserved 1:1):

  • § 1. Introduction — entirely
  • § 2.1-2.5 "Overview" — entirely
  • § 3.1 FR-REG-01..05 — the wording did not change
  • § 3.3 FR-DWL-1, FR-DWL-2 — the wording did not change
  • § 4.1-4.3 UC-REG-1, UC-UPL-1, UC-DWL-1 — headings and numbering
  • § 6. Data model — the structure of the two tables ("File attributes" +
    "Profile attributes") is preserved. I am NOT merging into one entity,
    NOT renaming file_ref to file_id, NOT creating a separate FILE entity
    with a duplicated content_hash. The structure is the analyst's zone,
    the meeting did not discuss it.
  • § 7 "Validation matrix" VAL-01, VAL-02, VAL-04..09 — entirely
  • § 8. Configurable parameters — entirely
  • § 9. Key parameters — except for the surgical fix SHA-256? → SHA-256

⚠️ Open questions (NOT auto-pasted into the document):

  • OQ-01: temporary-link TTL (NFR-SEC-02) — leaving it as "⚠️ TBD"
    in the existing baseline wording. The team did not name a number.
  • OQ-02: CreatorID format — leaving it as is in table 13.

────────────────────────────────────────────────────────────────
Confirm the plan or specify corrections.
Only after your OK will I write draft/SRS-v2.md.
```

### Step 5. The analyst confirms the plan

The analyst reads the diff plan in the chat — **the "Data model" section is preserved 1:1**, no rebuild into `7.1 Data Entities / 7.2 Data Dictionary` appeared. If something is wrong — corrects the plan in the chat. Confirms: `OK, apply`.

### Step 6. A4 writes SRS-v2.md with markers

Every new/changed line in the document carries a marker:
```markdown
#### FR-UPL-2 — Async file intake with a security queue *(new)*
- **Description:** ... [Source: meeting-notes.txt]
- ...

| VAL-03 | Hash | Value matches `^[a-f0-9]{64}$` *(changed: SHA-256? → SHA-256 confirmed)* | ... |
```

### Step 7. Standard recording and validation

```bash
uv run cli.py draft --project=fss-srs-augment --doc=SRS
# → status: validating

# AI prompt: "Run a2-requirements-validator for SRS-v2"
# A2 checks: the baseline is preserved, the markers are in place, the delta is consistent

uv run cli.py validate --project=fss-srs-augment --doc=SRS --version=2
uv run cli.py final --project=fss-srs-augment --doc=SRS --version=2
```

## 🔐 What exactly protects the analyst from "made-up content"

| Protection mechanism | Where it is wired in | What it blocks in this case |
|---|---|---|
| `rm_mode: augment` in the `context.md` frontmatter | A1 sets it, all agents must read it | The marker "this is not a draft from scratch, the baseline must not be touched" |
| `preserve_structure: true` | The same frontmatter | A direct ban on renaming sections, fields, entities |
| The ban on rebuilding the structure in A4 (rule 1) | `skills/rm/a4-document-writer.md`, the "Augment Mode" block | Would not have allowed merging the two attribute tables into `USER_PROFILE`, renaming `file_ref` → `file_id`, duplicating `content_hash` |
| Mandatory `*(new)*` / `*(changed: reason)*` marking | Same place, rule 2 | Any change is visible to the eye in the document; there are no "silent" edits |
| A diff plan in the chat with explicit confirmation | Same place, rule 3 | The analyst would have seen "I plan to rebuild section 6 into 7.1+7.2" — and would have said STOP |
| The soft checklist mode | Rule 4 | The `srs-checklist.md` checklist requires "7.1 Data Entities + 7.2 Data Dictionary". In augment this goes to an OQ rather than being auto-pasted into the document |
| The Master Orchestrator returns to `needs_revision` | `skills/rm/master-orchestrator.md` | If A4 did write the file without a diff plan/markers — the orchestrator will not let it through to `validating` |

## 🎓 The main rules for the team

1. **Do not use `cli.py draft` if a baseline exists.** That command is for writing from scratch. For extending — `cli.py augment`.
2. **Make A4 show the diff plan before writing the file.** If it silently saved `draft/<doc>-vN.md` without a diff plan in the chat — that is a contract violation. Roll back, ask again.
3. **Check the markers in the finished document.** In the augment output every new section/line must have `*(new: source)*` or `*(changed: reason)*`. The absence of markers = the baseline is preserved 1:1, and that must be true.
4. **The "Data model" section is the analyst's zone.** The AI does not rebuild it without an explicit request. If the AI proposes "improving the structure" in the diff plan — that is a normal proposal, but it requires your separate decision. Just `OK` to the plan as a whole does not confirm it.
5. **Open questions → into `## ❓ Open questions`, not into the document.** If the artifacts do not give a concrete value (TTL, CreatorID format), leave `⚠️ TBD` in the baseline; do not let the AI "guess".

## 📚 Related documents

- `flows/09-augment.md` — the formal flow description
- `skills/rm/a1-intake-analyst.md` — distinguishing baseline vs artifacts
- `skills/rm/a4-document-writer.md` — the "Augment Mode" block
- `skills/rm/master-orchestrator.md` — enforcing the contract
