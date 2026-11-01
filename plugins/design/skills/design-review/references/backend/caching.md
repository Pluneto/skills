# Caching review

A cache is a copy of data kept somewhere faster than the source of truth. Every caching concern answers one of two questions, and reviews should walk both:
- **A. The copy is wrong** (stale or mis-keyed): TTL, invalidation, write patterns, key design.
- **B. The copy is missing** (the load lands on the DB): stampede, avalanche, penetration, hot key, cold start.

Designs usually show the happy path and skip B. Always ask "what happens when the cache is empty?" and answer in requests/s against DB capacity.

## The arithmetic
- DB load = reads x (1 - hit rate). 10,000 reads/s against a DB that handles 5,000/s: a 90% hit rate leaves 1,000/s, 99% leaves 100/s.
- Popularity is usually skewed (a small share of items gets most reads), so rarely do you need to cache everything. A simple LRU typically reaches a lower hit rate than the ideal "cache the most popular N", because it infers popularity from history. Simulate the real access pattern rather than assuming.
- Size = items x bytes per item (e.g. 1M pages x 2 KB = 2 GB). Often the entire working set fits on one machine; check before proposing a cluster.

## Copy is wrong
- **Key design**: the key must include every dimension that changes the response (user, tenant, role, currency, locale, auth state). A missing dimension serves the wrong region or, for account pages, one user's data to another. That is a security bug; rank it as one. Put a version in the key so old copies become unreachable on a format change.
- **Write patterns**:
  - Write-back (write to cache, flush later): fastest, riskiest; a cache failure before the flush loses writes. Reject for data you can't lose.
  - Write-through (write DB and cache together): fresh cache, each write pays both.
  - Write-around (write only the DB): the old copy lingers until TTL or removal.
- **Invalidate by deleting, not updating.** Updating the cache on writes races: write A sets 100, write B sets 120, the DB ends at 120, but out-of-order cache updates can leave 100 until expiry. Deleting on every write is order-independent and idempotent; the next read refills. Residual race: a reader that loaded the old value before the write can put it back after the delete. Short TTLs bound this; leases or versioned values close it (see the Facebook memcache paper, "Scaling Memcache at Facebook", 2013).
- **TTL is worst-case staleness.** Fine for descriptions, wrong for stock counts during a sale.

## Copy is missing
| Failure | What happens | Defense |
|---|---|---|
| Stampede / thundering herd | A hot key expires; while the rebuild takes ~50 ms every concurrent read misses (20,000 reads/s means ~1,000 identical DB queries for one page) | Single-flight: the first miss takes a lock, others wait briefly or serve the old copy (1,000 queries become 1). Leases do the same across servers |
| Avalanche | Many keys expire together (100k keys loaded at startup with one TTL) | Jitter TTLs (e.g. +/-10% on one hour spreads expiry over ~12 minutes) |
| Penetration | Requests for nonexistent keys always miss and nothing is cached, so each one hits the DB (bug or attack) | Cache the negative result with a short TTL; a Bloom filter in front for floods of random ids |
| Hot key | One key on one shard gets far more than its neighbors; adding machines doesn't help | Replicate that key into several copies and pick one at random per read. Updates must touch all copies, so only for truly hot keys |
| Cold start / failover | A restart means every read misses; 10k/s into a 5k/s DB falls over | Warm popular keys before taking traffic, ramp traffic, make the app work (slower) with the cache absent, rate-limit rebuilds |

## Layers and distribution
- A CDN suits content identical for everyone and is useless or dangerous for per-user content unless keyed or varied correctly.
- Sharding keys by `hash mod N` remaps most keys (~80% going from 4 to 5 machines), an avalanche you caused; consistent hashing moves only the ~1/N the new machine takes over.
