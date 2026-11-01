# Observability review

The question: when this system misbehaves at 3 a.m., can someone tell what is wrong, where, and since when? Without that, every other finding in a review is a guess, and every capacity number goes stale unnoticed.

- **Per-route metrics**: request rate, error rate and latency as percentiles (p50, p95, p99), never only the average, because tail latency is what users and upstream timeouts feel. Break down by route template (`/users/:id`), not raw URL, and avoid labels with unbounded values such as user id or request id. Add a few business metrics (orders per minute, payment success rate): a silent drop is often a bug that returns 200.
- **Saturation shows trouble before errors do**: DB pool wait and connections in use versus pool size, queue depth and age of the oldest message, worker occupancy, cache hit rate.
- **Logs**: structured, one event per line, with a request/correlation id created at the edge and passed through every service, job and log line, so a user's report can be traced.
- **Slow-query log or statement statistics on in production**: usually the single most valuable backend performance signal (`data-access.md`).
- **Alerts** on symptoms users feel (error rate, latency percentile, queue age, failed payments) plus a few leading indicators (disk filling, pool near its limit, certificate expiry). Each alert has an owner and a first action; alerts nobody acts on hide real ones. Define an SLO for the key paths (e.g. 99.5% of checkout requests under 1 s) so "is it broken?" has an answer.
- **Health checks**: liveness (the process is up) and readiness (its dependencies are ok) are different; wiring a deep dependency check into liveness causes restart storms.
