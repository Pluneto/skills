# Reliability and overload review

The question: what happens when something is slow, down, or too busy? Most outages are not a component failing but a slow dependency exhausting threads, connections or memory in everything that calls it.

## Timeouts
- Timeouts follow the caller's budget: if the user-facing request has 2 s, the calls inside it must add up to less, and inner timeouts must be shorter than outer ones.

## Retries
- Retry only operations that are idempotent or protected by an idempotency key (`concurrency.md`). Retrying a non-idempotent charge is how double charges happen.
- Use exponential backoff with jitter and a small cap on attempts. Retry only errors that can succeed later (timeouts, 503, connection reset), never validation errors or 4xx.
- Retries multiply load: three attempts per layer across three layers is up to 27x on the dependency that is already struggling. Retry at one layer only, or use a retry budget (e.g. at most ~10% extra requests).

## Overload and backpressure
- Bound everything: queue lengths, concurrent requests, pool waits, request body size. An unbounded queue turns an overload into out-of-memory and very long latencies.
- **Shed load early**: when saturated, reject quickly with 429/503 and `Retry-After` instead of accepting work that will time out anyway. Serving some requests well beats serving all of them badly.
- Limit concurrency per dependency (bulkheads) so one slow dependency cannot consume every worker or connection.
- **Circuit breaker**: after repeated failures, stop calling the dependency for a short time and fail fast or use a fallback, then probe to recover.
- Queue-driven systems need a bound on consumer lag and a plan for when producers outrun consumers.

## Background work and queues
- Move work off the request path when the user doesn't need the result immediately: emails, exports, webhooks to third parties, image processing, fan-out.
- Delivery is at-least-once in practice, so consumers must be idempotent. Exactly-once is built from at-least-once plus idempotency.
- Decide the failure path: retry with backoff, then a dead-letter queue with alerting. Poison messages must not block the queue.
- Use the outbox pattern when a DB change must trigger a message, so the two cannot diverge (`data-access.md`).
- Long jobs need heartbeats or visibility timeouts so crashed workers' jobs get picked up, and a way to resume or safely re-run.
- Scheduled jobs on several servers run several times unless guarded by a lock or a single scheduler.

## Graceful degradation and recovery
- Decide what can be dropped when a dependency is down (recommendations, analytics, avatars) and what cannot (checkout, auth). Make the optional ones fail open and fast.
- The system must start with a cold or absent cache, an empty queue, or a restarted dependency (`caching.md`).
- Deploys: health checks that reflect readiness, graceful shutdown that drains in-flight requests, rolling deploys that tolerate two app versions at once (compatible schema changes).
- Backups are only real if a restore has been tested; state RPO (data you can lose) and RTO (time to recover).
- Single points of failure: list them. For each, say whether it is acceptable at this scale.
