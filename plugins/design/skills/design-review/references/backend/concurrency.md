# Concurrency review

## The bug shape
Nearly every concurrency bug is a **read followed by a write on shared data, with a gap between** (check-then-act, read-modify-write).
- One seat left, two buyers: both servers read "1 left", both confirm, the count ends at -1.
- A counter at 41 and two increments: A reads 41, B reads 41, B writes 42, A writes 42. Two increments, one effect (lost update). Two workers doing 1,000 unlocked increments each routinely end below 2,000.

A second CPU core is not required: a context switch at the wrong moment is enough. With async/await, an `await` between the check and the write still races. Search the code and design for this shape first, then pick a tool.

## Across multiple servers
An in-memory lock is invisible to other servers: two buyers on two servers each take their own lock, both read "1 left", both sell. In-process locks do not protect correctness across servers. Protection must live where all servers share it, usually the database.

- **Pessimistic locking**: lock first, assuming conflicts are likely. In a transaction, `SELECT ... FOR UPDATE` the row; the second reader waits, sees "sold", stops. Costs: waiting and deadlock risk, so keep transactions short and never hold them across network calls.
- **Optimistic locking**: no lock; check at write time with a version column:
  `UPDATE seats SET status='sold', version=8 WHERE id='F12' AND version=7;`
  Zero rows updated means someone else won: report "taken" or retry. Best when conflicts are rare. Under heavy contention on one row most attempts fail and retry, so switch to pessimistic locking or a queue.
- **Atomic SQL** often removes the gap entirely: `UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty > 0` and check the affected-row count. Prefer this to read-then-write whenever the rule fits in one statement.
- **Isolation levels**: the default (read committed in most databases) does not stop check-then-act across statements. Raise isolation to serializable and handle retries, or use one of the techniques above. Do not assume "it's in a transaction" means safe.
- **Distributed lock** (for something that isn't one DB row, e.g. a payment-provider call or a job one server may run): a lock in a shared service, with an expiry so a crashed holder doesn't block everyone. Expiry creates a new bug: A takes the lock, pauses (GC, network stall), the lock expires, B takes it and writes, A wakes believing it still holds the lock and writes. Fix with a **fencing token**: every grant carries an increasing number, and the storage layer rejects writes with a lower number than it has seen. Fencing only works if the storage layer checks the token; an expiring lock alone (typical Redis-style lock) is not safe for correctness, only for efficiency (avoiding duplicate work).
- **Idempotency** (locks don't solve this): a purchase succeeds, the reply is lost, the client retries, the server charges twice. The client sends a unique idempotency key; the server stores handled keys (with the saved response and a TTL, in the same transaction as the effect) and returns the saved result on repeats. The same applies to queue consumers and webhooks, which are delivered at least once.
