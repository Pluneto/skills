# Alternatives and decisions

The first design that lands on paper becomes the anchor: later reviews tend to polish it instead of questioning it. In planning, questioning it is cheap and is the most valuable thing a review does. Work through this file before settling on findings about details.

## 1. Challenge the requirements
Requirements written down early are often guesses, and a few of them usually drive most of the complexity. For each demanding requirement ask: who asked for it, what happens if it is relaxed, and what does it cost to meet?

- Typical cost drivers: real-time updates, strong consistency across regions, 99.99% availability, multi-region, per-tenant isolation, offline support, full audit history, handling card data yourself, "unlimited" scale.
- A requirement that costs a lot and protects little is worth pushing back on. Say so, and name the weaker version that would satisfy the real need ("updates within 5 s" instead of "real-time"; a payment provider's hosted checkout instead of handling card data).
- Also look for requirements that are missing: data deletion and retention, backup and recovery targets, who gets paged, abuse handling, cost ceiling, compliance regime.

## 2. Generate real alternatives
Produce two or three materially different designs for the core of the problem before judging any of them, and make each one something you would defend. A strawman next to a favourite is not a comparison. Include:
- the **simplest thing that could meet the requirements** (often fewer moving parts than the plan),
- the **design you would pick with no constraints on time or skills**, and
- the plan as written, if it is neither.

Axes along which designs differ (vary the ones that matter for this problem, not all of them):
- **Shape**: single deployable (monolith), modular monolith, separate services, serverless functions.
- **Platform**: managed backend platform (database, auth and storage as a service) vs framework on a managed host vs self-run infrastructure.
- **Data**: one relational database vs relational plus cache/search/queue vs several specialised stores; where the source of truth lives for each kind of data.
- **Interaction**: synchronous request/response vs queue or event-driven; polling vs push.
- **Build vs buy** for each commodity part: auth, payments, email, search, file storage, scheduling, feature flags. Buying is the default for anything security-critical or not your differentiator; check the pricing curve and the exit path.
- **Deployment**: one box, PaaS, containers on a managed orchestrator, self-run orchestrator.

## 3. Compare end states
Compare what each design looks like once built and running, not the distance from the current plan. Effort already spent on the plan is sunk, and so is anyone's attachment to it.

| Criterion | Question |
|---|---|
| Correctness by construction | Does the design make a bug class impossible (constraints in the database, tenant scoping enforced in one place, one writer per piece of state), or does it rely on every developer remembering? |
| Headroom | Capacity now / in 1 year / in 3 years; which resource saturates first; smooth degradation or a cliff? |
| Failure modes | What breaks when each dependency is slow or down; how large is the blast radius; how is data recovered? |
| Operating burden | Who deploys, upgrades, patches, restores, gets paged? How many things must someone understand to debug it at 3 a.m.? |
| Build effort | Time to a first working version and to full scope, for this team. |
| Cost | Infrastructure and vendor cost now and at 10x; shape of the pricing curve. |
| Lock-in and exit | How hard is it to leave: data export, standard interfaces, proprietary features leaking into code. |
| Reversibility | Which decisions are one-way doors (`design-now-vs-later.md`)? |

Name the one or two criteria that actually decide between the designs; a table of ticks with no verdict is not a review. Avoid false precision: weighted scores usually hide a judgment call instead of making it.

**Switching rule.** In planning, a change of approach costs an edit, so a better end state is reason enough to switch, even if the gain is modest. The condition is that the better design is not more complex to build and run than the one it replaces. Complexity is a cost of the end state: extra components, extra failure modes, extra things to learn. When the better design does cost more, show both with the delta (what is gained, what it costs) rather than choosing silently.

## 4. Tripwires and decision records
Give every major decision three short lines, so they stay current:
- **Why**: the requirement or constraint that tipped it.
- **Would change if**: a measurable signal and threshold (database CPU above 60% sustained at peak; checkout p95 above 800 ms; a second team writing to the same schema; a vendor tier costing more than X a month).
- **Then**: the migration path (what moves, in what order, with what downtime).

This lets the plan stay simple now without becoming a trap later, and turns "should we build X in advance?" into "we build X when signal Y fires".

## 5. Spikes: settle the biggest uncertainty before committing
When one assumption would sink a design if it were wrong, test it cheaply before the plan is final. There is nothing to measure yet, so build the smallest throwaway thing that tests the assumption: the data model with its five most important queries at 10x the expected data; the hottest endpoint under a realistic mix; a vendor's real limits (connections, rate limits, payload size, cold starts) and its price at 10x; a restore from backup; the hardest concurrency rule under parallel requests.

- **Pass criteria first.** Decide what "works" means before measuring. A reasonable default is p95 <= 500 ms, p99 <= 1 s and error rate < 1%, held for about 5 minutes or more. Check all three, since stacks fail differently.
- **Model users, not just requests.** Give simulated users a stated think time (a request every 3-10 s is about 0.1-0.3 req/s) and report requests/s next to "users". Use the real read/write mix: raising writes from a small share to a large share can cut capacity by a third or more.
- **Confirm the best candidate with a long run.** Short probes overstate capacity. Expect around 10% run-to-run noise, so gaps under 10% are ties.
- **State what the spike does not show**, since a prototype result is a rough floor, not final capacity.
