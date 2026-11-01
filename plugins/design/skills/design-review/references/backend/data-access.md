# Data access review

Most real backend bottlenecks are here, not in the language or the framework. Check this before proposing a cache, a new database, or more servers.

## What to look for
- **N+1 queries**: one query for a list, then one per row (often hidden behind an ORM's lazy loading or a per-item helper in a loop). Cost grows with page size and latency to the DB. Fix with a join, `WHERE id IN (...)`, or eager loading. Count queries per request on the hottest endpoints; double digits is a smell.
- **Missing or wrong indexes**: every frequent `WHERE`, `JOIN`, and `ORDER BY` should be served by an index. Composite indexes follow the leftmost-prefix rule (equality columns first, then range/sort). Run `EXPLAIN` (`EXPLAIN ANALYZE` on a copy) and look for sequential scans on large tables, sorts spilling to disk, and big gaps between estimated and actual rows. Check for functions on indexed columns (`WHERE lower(email) = ...`) and leading-wildcard `LIKE`, which defeat plain indexes.
- **Unbounded results**: lists with no `LIMIT`, endpoints returning whole tables. Deep `OFFSET` pagination scans and discards every skipped row; use keyset (cursor) pagination for large or growing lists.
- **Work in the wrong place**: filtering, sorting or aggregating in app code after fetching everything; or the reverse, an expensive aggregate recomputed on every request when it could be precomputed or incrementally maintained.

## Connection pools
- Every connection costs the DB memory and a process or thread. Total connections = app instances x pool size per instance; check it against the DB's limit. Hundreds of idle connections are usually a mistake.
- A bigger pool is not faster past the DB's useful parallelism (often a small multiple of its core count). Excess requests should queue in the app with a bounded wait, not pile onto the DB.
- Pool exhaustion shows up as errors or timeouts while the DB looks idle: slow requests hold connections (long transactions, an HTTP call made while holding a connection) and everyone waits. Set a pool acquire timeout so it fails fast instead of stalling.
- Serverless and many-instance deployments multiply connections; use an external pooler or a pooled-connection endpoint.
- Know what the driver does on connection reuse; per-reuse reset commands can cost real DB CPU at high request rates.

## Transactions
- Keep them short. Do not hold one open across network calls, user input, or slow computation: it holds locks and a pool connection the whole time.
- Group the writes that must succeed or fail together; do not wrap unrelated work in one big transaction.
- Know the isolation level in use and what it allows (`concurrency.md`).
- Long-running reports and batch jobs belong on a replica or off-peak, with their own connection limits.
- Multi-step workflows that span services cannot share one transaction: use an outbox (write the event in the same transaction as the data, publish it afterward) or a saga with compensations, and make steps idempotent.

## Schema and growth
- Pick types and constraints deliberately: unique constraints and foreign keys catch bugs the app misses and are often the last defense against duplicates.
- Plan for the biggest table: how large in a year, what is the retention policy, can old rows be archived or partitioned by time?
- Migrations on large tables can lock them. Check how the chosen engine handles adding columns and indexes (online/concurrent options), and use expand-then-contract changes so old and new app versions run against the same schema during a deploy.
- Reads that can tolerate staleness can go to read replicas; remember replication lag breaks read-your-own-write unless those requests are routed to the primary.
