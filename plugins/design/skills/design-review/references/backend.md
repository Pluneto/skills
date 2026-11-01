# Backend

Architecture, stack and database, data model, tenancy, capacity, caching, queues, races, reliability and security. Skip steps that clearly don't apply.

1. **Pin down workload and growth.** Peak and average requests/s, read/write ratio, data size now, in a year and in three, hot-key skew, topology (app servers, database co-located or not), durability (may the last commits be lost?), tenancy (do customers share data?), whether a duplicate action costs money, who operates it, hard constraints (compliance, budget, deadline, skills). Take what the repo or plan states; state the rest as Assumptions with the default you used.
2. **Do the capacity arithmetic.**
   - Users to requests/s only with a stated request rate per user (a person clicking every few seconds is roughly 0.1-0.3 req/s; a polling client is far more).
   - Database load = reads × (1 − cache hit rate): a 90% hit rate cuts load 10×, 99% cuts it 100×.
   - Size = items × bytes per item; check whether the whole working set fits on one machine before designing a cluster.
   - Compare with the target now, at 10×, and in one and three years, and find the **first cliff**: which resource saturates first, and does it degrade smoothly or fall off? Numbers beat adjectives: a cache or lock added without the arithmetic usually solves the wrong problem.
   - Report it as a **Capacity and horizon** block right after Assumptions: the numbers now / 1 year / 3 years, the first cliff, your confidence.
3. **Settle the one-way doors.** Data model and IDs, tenancy, identity and permissions, API contracts, consistency boundaries, data lifecycle, where state lives. Decide these on purpose now; for everything else choose the simplest option that keeps the door open ([backend/design-now-vs-later.md](backend/design-now-vs-later.md)).
4. **Check correctness and security first.** Double-sell, lost update and another tenant's data fail at any load, so they outrank performance findings. Find every read-decide-write gap and check it survives multiple servers and retries ([backend/concurrency.md](backend/concurrency.md)). Check authorization on every object access and every cache key ([backend/security.md](backend/security.md)).
5. **Review the relevant pieces.**

   | Topic | Read |
   |---|---|
   | Requirements, alternatives, tripwires, spikes and their pass criteria | [backend/alternatives-and-decisions.md](backend/alternatives-and-decisions.md) |
   | What to decide now vs defer, retrofit cost | [backend/design-now-vs-later.md](backend/design-now-vs-later.md) |
   | Races, locking, double-charge, idempotency | [backend/concurrency.md](backend/concurrency.md) |
   | Cache design and failure modes | [backend/caching.md](backend/caching.md) |
   | Slow queries, schema, indexes, N+1, pools, transactions | [backend/data-access.md](backend/data-access.md) |
   | Language, framework, database choice, per-request overhead, SQLite vs server database | [backend/stack-and-database.md](backend/stack-and-database.md) |
   | Timeouts, retries, queues, overload, graceful degradation | [backend/reliability.md](backend/reliability.md) |
   | Authn/authz, tenant isolation, input handling, abuse limits, secrets | [backend/security.md](backend/security.md) |
   | Can you tell what is wrong in production? | [backend/observability.md](backend/observability.md) |

6. **Run a pre-mortem.** Assume the project failed or was rewritten a year from now: the five likeliest reasons, and the change to the plan or tripwire that covers each. Typical sources: a one-way door chosen casually, a requirement that turned out wrong, an operational burden nobody owned, a vendor limit or price change, a money or permissions bug, growth in one table or tenant.
7. **Write the revised plan into Decisions for the plan**: what to build now, what to decide now but build later, what to leave out, each deferred piece with its tripwire and migration path.
8. **Name the spikes.** Where the capacity gap is large or an assumption is load-bearing, the one or two spikes that settle it before committing, each with pass criteria, go into Checks for Done when (as the first milestone's checks).

Finding severities for this domain, highest first: correctness or security flaw; one-way-door risk; fails at the target load or horizon; operating or complexity burden; inefficiency.
