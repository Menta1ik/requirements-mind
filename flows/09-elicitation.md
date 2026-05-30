# Flow: 09-elicitation (Gathering requirements from scratch / Elicitation Mode)

This flow describes the interactive process of gathering requirements from scratch, when the analyst has only a raw idea and no ready-made input materials. The flow is based on the hybrid **"Pragmatic Analyst"** standard (JTBD + Use Cases + ISO 29148).

---

## 👥 Roles involved
* **A3 — Elicitation Expert** (AI requirements interviewer)
* **Onboarding Wizard (A0)** (AI project-start assistant)
* **Systems analyst** (the user)

---

## 🏁 Inputs
* A raw business idea or a short project name, provided by the analyst in the IDE chat.
* An empty `input/` folder, or only basic templates present.

---

## ⚙️ Step-by-step process

### 🌟 Step 1: Activate Elicitation mode
1. The analyst starts a session with the AI assistant:
   > **"Mary, let's start gathering requirements for the new project delivery-app"**
2. The AI assistant checks the project state in `state.json` (or creates the folder structure if the project is brand new).
3. The AI assistant routes the session to the **`a3-elicitation`** skill and sets `profile: 6` in `state.json`.

---

### 💬 Step 2: Interactive dialogue (requirements gathering)
1. **JTBD phase (business value):**
   * The `a3-elicitation` AI agent asks about the target audience and formulates Jobs-to-be-Done hypotheses:
     * *"When I want to order food, I want to see the delivery time, so that I can plan my lunch"*.
   * The analyst confirms or corrects the wording.
2. **Use Cases phase (functionality):**
   * The AI agent interviews the analyst about the system boundaries and the key user scenarios.
   * The main functional blocks are identified (for example, Catalog, Cart, Payment, User account).
3. **ISO 29148 NFR phase (system requirements):**
   * The AI agent interviews the analyst about non-functional requirements: security (authentication, encryption), performance (RPS, response time), and integrations with external APIs.

---

### 📝 Step 3: Auto-generate the requirements on disk
As soon as the session is complete (all key aspects have been discussed), the AI agent:
1. Writes a structured file **`projects/<project-name>/input/requirements.md`** with all the details (including JTBD, functional blocks, Use Cases, NFR).
2. Writes an initial starter skeleton **`projects/<project-name>/context.md`** with references to `input/requirements.md`.
3. Sets the project status to `status: "onboarding"` with `profile: 6` and `active_agents: ["a0", "a3"]` in `state.json`.

---

### 🏁 Step 4: Record and move on to specification development
Once the AI has generated the files, the AI agent automatically proposes running the onboarding-completion command in the terminal (the analyst just confirms the run in the chat):

```bash
# RUN AUTOMATICALLY BY THE AI AGENT AFTER CONFIRMATION IN THE CHAT
uv run cli.py onboard --project=<project-name>
```

**What happens:**
* The CLI checks that `input/requirements.md` and `context.md` are present.
* The CLI moves the project status to **`intake`**, inviting you to run a deep Intake analysis with `a1-intake-analyst` to proceed to creating the BRD.
