# API contracts

Any surface other code calls: HTTP endpoints, server actions and RPC functions, webhooks in and out, events on a queue, a CLI, a database function other services use. A contract a client you can't force to update depends on (a mobile app, a partner, a bot, a published CLI) is a one-way door.

## Checks

- **Shape and naming.** Resources and fields named in the domain's own words (the repo's glossary), consistently across endpoints. One way to say a thing: not `userId` here and `member_id` there.
- **Compatibility.** Changes are additive: new optional fields, new endpoints. A field never changes meaning or type; removing one goes through a deprecation window with a date. Clients ignore unknown fields. A version scheme exists before the first external client.
- **Unsafe operations are idempotent.** Every create, pay, send or transition accepts an idempotency key or is naturally idempotent (a PUT of the full state, a transition guarded by the current state), so a retry or double click does not do it twice. Webhook receivers deduplicate by the sender's event ID.
- **Authorization per operation.** Every operation checks that the caller may act on *this* object (ownership, role, tenant), on the server, defaulting to deny. Internal, admin and server-action endpoints included: a server action is a public endpoint.
- **Validation at the boundary.** Every input is parsed against a schema (type, range, length, enum) before use, and rejected with a field-level error. Nothing from the client is trusted for identity, price or permissions.
- **Errors.** One error shape everywhere: a stable machine-readable code, a human message that says what to fix, the failing field. Status codes mean what they say (400 bad input, 401/403 auth, 404, 409 conflict such as "sold out" or "already done", 422, 429, 5xx only for server faults).
- **Lists.** Cursor pagination with a stable sort and a maximum page size; filters and sorting named, not free SQL.
- **Values.** Money as integer minor units plus currency. Times in ISO 8601 UTC, with the time zone kept where it matters (an event's local start). IDs opaque strings, never sequential numbers that leak counts or invite guessing.
- **Limits and time.** Rate limits per caller with 429 and `Retry-After`. Every call out has a timeout; long work returns at once with a job ID and status to poll or a webhook to receive.
- **Webhooks out.** Signed payloads (HMAC with a timestamp against replay), retries with backoff, events that may arrive twice or out of order, carrying an ID and a version.
- **Partial failure.** A batch says per item what succeeded; a multi-step operation is atomic or has a defined compensating step.
- **Contract as a file.** The schema lives in one source (OpenAPI, a typed schema, generated types) that tests run against, so the docs and the code can't drift.

## Typical Checks for Done when

- "Repeating the same purchase request with the same idempotency key creates one order."
- "Calling the endpoint as another member's account returns 403/404 and changes nothing."
- "Every error response matches the error schema (contract test)."
