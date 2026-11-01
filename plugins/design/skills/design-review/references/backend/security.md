# Security review (design level)

A design review checks the structural mistakes that are expensive to fix later. It does not replace a penetration test or a dependency scan. Rank findings here as correctness bugs: they fail at any load.

## Authentication
- Prefer a mature identity provider over rolling your own.
- Rate-limit login, signup, password reset and OTP endpoints, with generic error messages that don't reveal whether an account exists.

## Authorization (the most common serious flaw)
- **Check ownership on every object access**, not only that the user is logged in. `GET /orders/123` must verify order 123 belongs to the caller (or the caller's tenant). Missing checks (IDOR / broken object-level authorization) are the top API vulnerability. Sequential ids make it trivially exploitable; unguessable ids are not a substitute for the check.
- Check field-level access too (can this role set `is_admin` or `price`). Mass assignment: never bind request bodies straight onto models without an allowlist of fields.
- Centralize the rule (middleware, policy layer, or database row-level security) so it cannot be forgotten on a new endpoint, admin and internal routes included. Ask what the default is: deny or allow.

## Multi-tenancy
- Every query on tenant data must be scoped by tenant, enforced in one place (query layer, row-level security) rather than remembered by each developer.
- Check caches, queues, file storage paths, search indexes, logs and background jobs for tenant leakage. A cache key without the tenant or user is a data leak (`caching.md`).

## Input and exposure
- Use parameterized queries everywhere, with an allowlist for `ORDER BY` and column names taken from input. Block internal and metadata addresses when the server fetches user-supplied URLs (SSRF), and verify the signature and timestamp on webhooks you receive.
- Rate limit by identity and IP, with stricter limits on expensive and unauthenticated endpoints. Limits kept in one server's memory don't apply across servers.
- Expensive operations (exports, search, report generation, large fan-out) are denial-of-service vectors; bound or queue them.

## Secrets and data
- Secrets live in a secret manager or environment, never in the repository or client code; they can be rotated and differ per environment.
- Least privilege: the app's DB user should not own the schema or be a superuser; separate credentials for migrations.
- Decide what personal data you store at all, how long, and how it is deleted. Don't log secrets, tokens, full card numbers, or personal data without need.
