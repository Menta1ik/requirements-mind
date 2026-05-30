# BRD Checklist

Used by agent A2 to validate the Business Requirements Document.
Based on: ISO/IEC/IEEE 29148:2018, BABOK v3, PMBOK 7.

## Augment policy (how to read the "Required" column)

As of v2.2, each section is assigned an **augment-policy** for the case where the document is being extended from a baseline (`rm_mode: augment`):

- `required` — a critical, meaning-bearing section. **Mandatory in any mode.** If it is absent in the baseline, A2 assigns `FAILED`. These are the sections on business goals, measurable metrics, scope, key stakeholders — without them the document has no value.
- `optional-augment` — a recommended, form-bearing section. In `draft` mode it is mandatory (`FAILED`); in `augment` mode its absence is reported as a **warning** in the "⚠️ Augment-soft" block of the validation report, but does not block the transition to `approved`. These are sections that in a baseline may be named differently or embedded in other sections.
- `if-applicable` — an "as applicable" section. If the business context requires it, it is mandatory; otherwise it is skipped. No difference between modes.

A2 determines the mode via the `context.md` frontmatter (`rm_mode: draft | augment`).

## Mandatory sections

| Section | Required | Augment-policy | Completeness criterion |
|---|---|---|---|
| 0. Document Control | ✅ | optional-augment | Version, status, author, approvers, revision history |
| 1. Executive Summary | ✅ | required | Problem Statement + Proposed Solution present |
| 2.2 Business Problem | ✅ | required | The problem is stated clearly, not vaguely |
| 2.3 AS-IS | ✅ | optional-augment | The current state is described |
| 2.4 TO-BE | ✅ | optional-augment | The desired state is described |
| 2.5 Gap Analysis | ✅ | optional-augment | The gap between AS-IS and TO-BE is stated |
| 3.1 In Scope | ✅ | required | At least 3 items |
| 3.2 Out of Scope | ✅ | required | At least 2 items (what is explicitly NOT included) |
| 3.3 Assumptions | ✅ | required | At least 3 assumptions |
| 3.4 Constraints | ✅ | required | At least 2 constraints |
| 4.1 Stakeholder Register | ✅ | required | Table: role, name/title, interests, influence |
| 4.2 RACI Matrix | ✅ | optional-augment | All roles from the Stakeholder Register are covered |
| 5.1 Business Goals | ✅ | required | SMART format, at least 2 goals |
| 5.3 Success Criteria / KPIs | ✅ | required | Measurable metrics (not "improve", but "+20% in 6 months") |
| 5.4 Business Rules | ✅ | required | At least 3 rules |
| 5.5 Functional Requirements | ✅ | required | High level, at least 5 requirements |
| 5.6 Non-Functional Requirements | ✅ | required | Mentioned: performance, security, availability |
| 5.7 Data Requirements | ⚠️ | if-applicable | If the system works with data — mandatory |
| 5.8 Compliance & Regulatory | ⚠️ | if-applicable | If applicable — mandatory |
| 6.2 High-level Use Cases | ✅ | optional-augment | Table: ID, name, actor, goal, priority |
| 7.1 Risk Register | ✅ | required | At least 3 risks with mitigation |
| 7.2 Open Issues | ✅ | optional-augment | All open issues with an owner and a deadline |
| 8. Glossary | ✅ | optional-augment | All domain-specific terms from the text |

## Requirements quality

- [ ] No contradictions between sections
- [ ] All terms from the text are in the Glossary
- [ ] All stakeholders from RACI are in the Stakeholder Register
- [ ] All goals from section 2 are covered in section 5
- [ ] No assumptions hidden in the text (all are moved into 3.3)
- [ ] No open issues without an owner and a deadline
- [ ] Business Goals are in SMART format
- [ ] KPIs are measurable (numbers, percentages, deadlines)

## Blocking problems (FAIL)

The document gets a FAIL status if:
- Any section with `augment-policy: required` is missing (in any mode).
- In `rm_mode: draft` — any section with `augment-policy: optional-augment` is missing.
- Business Goals are not measurable.
- There is no In Scope / Out of Scope.
- There is no Stakeholder Register.
- There is no Risk Register.
- There are direct contradictions between sections.

In `rm_mode: augment` mode, the absence of `optional-augment` sections → a **warning** in the "⚠️ Augment-soft" block of the report, not a blocker.
