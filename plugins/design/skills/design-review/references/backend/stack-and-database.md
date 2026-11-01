# Stack and database choice

Use this to understand mechanisms and orders of magnitude. Figures here are illustrative orders of magnitude from small single-node setups, not a ranking; they will not choose the stack for you, and the review still has to land on a recommendation. Decide on requirements and long-term costs (`Choosing a foundation` below, `alternatives-and-decisions.md`), use the figures only to check that the choice has headroom, and test the real workload before committing (spikes in `alternatives-and-decisions.md`).

## Principles
- **Architecture usually beats language.** Per-request machinery (process model, framework boot cost, middleware, dependency injection, serialization, driver behavior) is where the time goes. In public single-node benchmarks, the same language moved by an order of magnitude when framework layers were removed or the process model changed (per-request boot to a long-running server, fresh connections to reused ones and prepared statements), far more than the gap between languages. When a stack looks slow, profile that layer before proposing a rewrite.
- **Shared dependencies set a common wall.** If two different languages hit the same ceiling, the shared component (typically the database on the same core) is the limit. Check the CPU split per process before concluding anything about languages.
- **Fixed overhead hides in defaults.** A driver that resets the session on every pooled-connection reuse, a framework that boots on every request, or a middleware chain on every call can dominate cheap endpoints. Near-identical throughput for a trivial and a heavy endpoint is the tell.

## Database choice

### Server database vs embedded SQLite
- **SQLite wins when the app and DB are on one node**: no server process, no socket or protocol round trip, so CPU goes to the app. Same-box comparisons often show roughly 2x capacity versus a server database for the same app. A good fit for single-node apps, tools, edge deployments, read-heavy sites.
- **Durability setting dominates the comparison.** WAL with `synchronous=NORMAL` survives an app crash but can lose the latest commits on power loss. With `synchronous=FULL`, a write-heavy load can collapse because SQLite has a single writer and each commit waits for the disk sync serially. Server databases use group commit, so concurrent durable writes share a flush. Never compare databases at unequal durability.
- **Choose a server database** (Postgres, MySQL, MariaDB) when you need replication and failover, several app servers writing, heavy concurrent durable writes, or the ecosystem (extensions, tooling, managed hosting). That machinery costs overhead that is invisible in a single-box benchmark but is what availability needs.
- SQLite has no built-in replication; a node loss is a data-loss or restore-from-backup event unless you add a replication layer. Decide if that is acceptable.

### Between server databases
- In published same-box tests the mainstream relational databases landed within the same tier, with differences of tens of percent that moved with workload mix, dataset size and default settings (for example a monitoring schema on by default, or different disk-write behavior). That is not enough to switch on performance alone.
- Choose on features, operations, team skill and ecosystem: replication options, JSON and indexing capabilities, extensions, managed offerings, licensing.
- Apply the same basic tuning to each before comparing (buffer pool around 25% of RAM as a starting point, comparable durability).
- SQL vs NoSQL is a data-model question (access patterns, consistency needs, query flexibility), not a speed contest. Start from how the data is queried and what must be transactional.

### Write mix matters
Raising writes from a small share to a large share of requests can shift the bottleneck from CPU to disk IO and cut capacity by roughly a third to a half. Always ask for the read/write ratio.

## Choosing a foundation (planning)
- **Start from requirements, not from a default.** Data model and access patterns, transaction and consistency needs, write volume and durability, number of writers and app servers, availability target, who operates it, compliance and data residency, expected size in three years, cost curve at 10x.
- **The mainstream choice is the prior to beat, not a shield.** A mainstream framework with a server relational database (often managed) wins on hiring, tooling, documentation and operating knowledge, and most products never outgrow it. Beat it when a requirement says so: embedded SQLite for a read-heavy single-node app, a document or wide-column store for an access pattern that is truly non-relational, a managed backend platform when team capacity is the binding constraint. Name the requirement that tipped the choice.
- **Count the operating cost.** Managed vs self-hosted decides who handles backups, failover, upgrades and patching. A cheaper-looking self-run option is often the more expensive end state.
- **Test the choice beyond today.** Check it at 10x data and at the next team size, check the exit path (standard SQL, data export, open source or not), and check where vendor-specific features will leak into business code.
- **Prefer a long-running process model over per-request boot** when endpoints are light.
