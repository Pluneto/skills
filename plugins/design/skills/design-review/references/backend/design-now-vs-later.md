# Design now, build later

Some decisions are cheap to change late and some are not. In planning, spend the scrutiny on the second kind, and for the first kind choose the simplest option that doesn't close doors. The test for each item: **what would it cost to change this once real data, real clients and a running team depend on it?**

## One-way doors: decide on purpose now
These touch every table, endpoint, client or cache entry, so retrofitting means a migration with downtime risk and a long tail of missed spots.

- **Data model and identifiers.** Entity boundaries and who owns each piece of data (a single source of truth). IDs: opaque and never trusted from the client, time-sortable if you will paginate by them, never reused, carrying no meaning. Money as integer minor units plus currency, never floats. Timestamps in UTC, with the time zone stored where it matters. Unique, foreign-key and check constraints from the first migration: they are the last defense against duplicates and orphans, and adding them to dirty data is painful (`data-access.md`).
- **Tenancy.** Is there more than one customer or organisation? If yes: the tenant column on every tenant-owned table, enforced in one place (row-level security or a query layer), and the tenant in every cache key, job payload and storage path, from day one (`security.md`). Pick the isolation model (shared tables, schema per tenant, database per tenant) by compliance and noisy-neighbour needs.
- **Identity and permissions.** Identity provider; the user / organisation / role / resource model; a central policy layer so a new endpoint is denied by default. Leave room for account linking, invitations and SSO even if they ship later. Bolting authorisation onto finished endpoints is how ownership checks get missed (`security.md`).
- **API contracts.** Anything a client you cannot force to update depends on (mobile apps, partners, a public API) is permanent: versioning scheme, cursor pagination, a consistent error shape, idempotency keys on every unsafe operation (`concurrency.md`), rate-limit signalling, stable field names.
- **Consistency and transaction boundaries.** Which operations must be atomic, which may be eventually consistent, and where the source of truth for each fact lives. Outbox for events that must match a database change, idempotent consumers, versioned event schemas (`data-access.md`, `reliability.md`). Retrofitting idempotency into a running payment flow is a bad week.
- **Data lifecycle.** Retention and deletion (including user erasure requests), which personal data is stored at all, backup and restore targets (RPO/RTO) with a tested restore, audit-trail needs. Soft vs hard delete changes every query.
- **Where state lives.** Keep application servers stateless: no correctness-critical state in process memory or on local disk; sessions in tokens or the database; files in object storage with the database holding references. This keeps horizontal scaling and zero-downtime deploys available later (`concurrency.md`).
- **Vendor and platform coupling.** Note where proprietary features leak into business code. Wrap them behind a thin interface only where exit is costly and a move is plausible; wrapping everything is its own waste.

## Safe to defer, but keep the door open
Do not build these until the tripwire fires; do make sure nothing in the design prevents them.

| Deferred | Keep open by | Typical tripwire |
|---|---|---|
| Caching layer | One data-access layer; cache-friendly keys; stateless app | Database CPU or latency at peak above target after queries are fixed |
| Read replicas | Reads that tolerate staleness are identifiable; read-your-own-write goes to the primary | Read load saturating the primary |
| Queue / background workers | Slow or third-party work isolated behind a function boundary; idempotent handlers | Request path blocked by slow work; fan-out; retries needed |
| Search engine | Search behind one interface; data changes observable | Database full-text no longer meets quality or load |
| Analytics store | Events or change capture possible; reporting queries kept off the primary | Reports slowing production queries |
| Partitioning / sharding | Partition-friendly keys (tenant or time); no cross-tenant joins on hot paths | Largest table exceeds what one node handles comfortably |
| Service split | Clear module boundaries and data ownership inside the monolith | Independent scaling or release cadence is a real, recurring need |
| Multi-region | Region-agnostic IDs; data residency known | A stated availability or latency requirement one region cannot meet |
