# SRS Checklist

Used by agent A2 to validate the Software Requirements Specification.
Based on: ISO/IEC/IEEE 29148:2018, IEEE 830, BABOK v3.

## Augment policy (how to read the "Required" column)

As of v2.2, each section is assigned an **augment-policy** for the case where the document is being extended from a baseline (`rm_mode: augment`):

- `required` — a critical, meaning-bearing section. **Mandatory in any mode.** If it is absent in the baseline, A2 assigns `FAILED`. These are: functional requirements with IDs, measurable NFRs, Use Cases with alternatives, the integrations table.
- `optional-augment` — a recommended, form-bearing section. In `draft` mode it is mandatory (`FAILED`); in `augment` mode its absence is reported as a **warning** in the "⚠️ Augment-soft" block of the validation report. These are sections with a particular form (Data Entities as a separate 7.1, Operating Environment as a separate 2.4) — in a baseline they may be embedded in other sections or have different headings.
- `if-applicable` — an "as applicable" section. No difference between modes.

A2 determines the mode via the `context.md` frontmatter (`rm_mode: draft | augment`).

## Traceability to the BRD (checked first)

- [ ] All Business Goals from the BRD are covered by at least one FR
- [ ] All Business Rules from the BRD are reflected in an FR or NFR
- [ ] All Stakeholders from the BRD have a User Class in section 2.3
- [ ] All In-Scope items from the BRD have an FR or Use Case
- [ ] No FR contradicts the BRD Constraints
- [ ] The SRS scope does not exceed the BRD scope

> **Note:** traceability to the BRD is `required` in any mode. Business Goals without FR coverage are always FAILED.

## Mandatory sections

| Section | Required | Augment-policy | Completeness criterion |
|---|---|---|---|
| 0. Document Control | ✅ | optional-augment | Version, status, link to the BRD |
| 1.2 Scope | ✅ | required | What the system does AND does not do |
| 1.3 System Overview | ✅ | optional-augment | A context diagram or description |
| 2.3 User Classes | ✅ | required | All roles from the BRD Stakeholders are covered |
| 2.4 Operating Environment | ✅ | optional-augment | OS, browsers, environments |
| 2.6 Assumptions & Dependencies | ✅ | required | Technical assumptions + those from the BRD |
| 3. Functional Requirements | ✅ | required | Each FR: ID, description, MoSCoW, source in the BRD, verification criterion |
| 4.1 Performance | ✅ | required | Concrete metrics (ms, RPS, concurrent users) |
| 4.2 Reliability & Availability | ✅ | required | SLA uptime %, MTTR |
| 4.3 Security | ✅ | required | Auth, encryption, audit logs |
| 4.4 Usability | ⚠️ | if-applicable | If applicable |
| 5.2 System Interfaces | ✅ | required | Integrations table |
| 6. Use Cases | ✅ | required | Happy Path + alternatives + error scenarios |
| 7.1 Data Entities | ✅ | optional-augment | The main entities (in a baseline this may be called "Data Model" — that is acceptable) |
| 7.2 Data Dictionary | ✅ | optional-augment | Data types, formats, constraints (in a baseline this may be a table inside another section) |
| 8. Verification Table | ✅ | required | Each FR and NFR has a verification method |
| Glossary | ✅ | optional-augment | All terms from the text |

## Requirements quality

- [ ] Each FR has a MoSCoW priority
- [ ] NFRs contain measurable metrics (not "fast", but "P95 < 200ms")
- [ ] Each Use Case has a Happy Path + at least 1 alternative + error scenarios
- [ ] No FR without a verification criterion
- [ ] No duplicate requirements
- [ ] No requirements that cannot be verified
- [ ] All Use Cases are linked to an FR
- [ ] All terms are in the Glossary

## Blocking problems (FAIL)

The document gets a FAIL status if:
- Any section with `augment-policy: required` is missing (in any mode).
- In `rm_mode: draft` — any section with `augment-policy: optional-augment` is missing.
- Any Business Goal from the BRD is not covered by an FR.
- Any FR without a MoSCoW priority.
- Any NFR without a measurable metric.
- There is no integrations table.
- There is no Verification table.
- There are direct contradictions with the BRD.

In `rm_mode: augment` mode, the absence of `optional-augment` sections → a **warning** in the "⚠️ Augment-soft" block of the report, not a blocker.
