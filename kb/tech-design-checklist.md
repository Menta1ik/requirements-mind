# Checklist: Technical Design Document

This checklist is used by the **A2 Validator** agent to check the completeness of the technical design, and by the **A4 Writer** agent as a template for generating the document.

## Augment policy (how to read the checklist)

As of v2.2, each section is tagged with `[required]` or `[optional-augment]` after the heading:

- `[required]` — a critical, meaning-bearing section. **Mandatory in any mode.** Its absence → `FAILED`. These are: the DB schema, the authentication/authorization strategy, the target performance metrics, data encryption.
- `[optional-augment]` — a recommended, form-bearing section. In `rm_mode: draft` it is mandatory (`FAILED`); in `rm_mode: augment` its absence → a **warning** in the "⚠️ Augment-soft" block, not a blocker. These are: diagrams (may be embedded in the text in a baseline), a formal description of the architectural pattern (if the baseline already records it — do not duplicate), a description of migrations.

A2 determines the mode via the `context.md` frontmatter (`rm_mode: draft | augment`).

---

## 1. General information and architectural style `[optional-augment]`
- [ ] The overall architectural pattern is described (monolith, microservices, serverless, CLI-first).
- [ ] The choice of the technology stack is justified (programming languages, frameworks, DBMS).
- [ ] The key system components and the boundaries of their responsibility are described.

---

## 2. Data architecture and DBMS `[required]`
- [ ] The database schema is described (tables, relationships, indexes, field types). `[required]`
- [ ] A Mermaid ER diagram of entity relationships is provided. `[optional-augment]`
- [ ] The data migration and schema versioning strategy is described. `[optional-augment]`
- [ ] Requirements for DBMS backup and fault tolerance are documented. `[required]`

---

## 3. Components and integrations `[required]`
- [ ] Sequence Diagrams are provided for the key user scenarios. `[optional-augment]`
- [ ] Internal and external integrations are described (message queues, external APIs, caching). `[required]`
- [ ] The interaction protocols are specified (REST, gRPC, WebSockets). `[required]`

---

## 4. Security and standards compliance `[required]`
- [ ] The authentication and authorization protocol is documented (JWT, OAuth2, sessions). `[required]`
- [ ] The access-control policy is described (RBAC/ABAC). `[required]`
- [ ] Requirements for data encryption at rest and in transit are specified. `[required]`
- [ ] Mechanisms for logging critical security and audit events are described. `[required]`

---

## 5. Performance and scaling `[required]`
- [ ] Target performance metrics are defined (Response Time, throughput, SLA). `[required]`
- [ ] The data-caching strategy is described. `[optional-augment]`
- [ ] Horizontal and vertical scaling mechanisms are specified. `[required]`
- [ ] Peak-load handling and system self-recovery mechanisms are described (Circuit Breaker, Rate Limiting). `[required]`

---

## Blocking problems (FAIL)

The document gets a FAIL status if:
- Any `[required]` item is missing (in any mode).
- In `rm_mode: draft` — any `[optional-augment]` item is missing.

In `rm_mode: augment` mode, the absence of `[optional-augment]` items → a **warning** in the "⚠️ Augment-soft" block of the report, not a blocker.
