# Checklist: API Contract

This checklist is used by the **A2 Validator** agent to check the completeness of the API specifications, and by the **A4 Writer** agent as a template for generating the document.

## Augment policy (how to read the checklist)

As of v2.2, each section is tagged with `[required]` or `[optional-augment]` after the heading:

- `[required]` — a critical, meaning-bearing section. **Mandatory in any mode.** These are: the list of endpoints with their methods and parameters, the response models and error codes, the authorization scheme.
- `[optional-augment]` — a recommended, form-bearing section. In `rm_mode: draft` it is mandatory; in `rm_mode: augment` its absence → a **warning** in the "⚠️ Augment-soft" block, not a blocker. These are: common headers (may be recorded once in a baseline and not repeated per endpoint), curl/OpenAPI examples (if the baseline already includes an OpenAPI spec alongside — it is acceptable not to duplicate).

A2 determines the mode via the `context.md` frontmatter (`rm_mode: draft | augment`).

---

## 1. Basic API information `[required]`
- [ ] The base URL and the supported API versions are specified (versioning via URL or headers). `[required]`
- [ ] The data formats used are described (JSON, XML, Protocol Buffers). `[required]`
- [ ] The common HTTP request and response headers are documented (for example, `Content-Type`, `Authorization`). `[optional-augment]`

---

## 2. Endpoint specification (Endpoints) `[required]`
- [ ] The HTTP method is specified for each endpoint (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`). `[required]`
- [ ] All query parameters, path parameters, and their data types are described. `[required]`
- [ ] A full Request Body example is provided, with a description of which fields are mandatory. `[required]`
- [ ] Input-data validation is described (maximum length, string formats, number ranges). `[required]`

---

## 3. Response models and status codes `[required]`
- [ ] Detailed examples of successful responses are provided (for example, HTTP 200 OK, 201 Created). `[required]`
- [ ] Examples of all possible errors are documented (for example, HTTP 400 Bad Request, 401 Unauthorized, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error). `[required]`
- [ ] Errors are formatted strictly per the RFC 7807 standard (Problem Details). `[optional-augment]`

---

## 4. Security and limits `[required]`
- [ ] The authorization scheme is specified for each endpoint (whether authorization is required, which token type). `[required]`
- [ ] The rate-limiting policy for the endpoints is documented. `[required]`

---

## 5. Interactive examples `[optional-augment]`
- [ ] Working call examples are provided via `curl` or a specification in OpenAPI / Swagger 3.0 format. `[optional-augment]`

---

## Blocking problems (FAIL)

The document gets a FAIL status if:
- Any `[required]` item is missing (in any mode).
- In `rm_mode: draft` — any `[optional-augment]` item is missing.

In `rm_mode: augment` mode, the absence of `[optional-augment]` items → a **warning** in the "⚠️ Augment-soft" block of the report, not a blocker.
