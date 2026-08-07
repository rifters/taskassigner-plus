# Rigor Profile

**Tier:** External-facing

Customers or the public; untrusted users; higher stakes. Trust and safety — assume adversarial users.

---

## Access / Auth

Full authentication + authorization. Account lifecycle (signup, password reset, lockout). Treat every request boundary as untrusted.

## Multi-user / Tenancy

Multi-tenant isolation where multiple customers/orgs share the system — no cross-tenant data leakage.

## Data Sensitivity

Treat all user data as sensitive. PII handling, encryption in transit, least privilege, and a clear view of compliance obligations.

## Security

Explicit threat model; rate limiting and abuse prevention; injection/XSS/CSRF/SSRF defenses; dependency hygiene; secrets management; logging that never leaks PII.

## Validation & Tests

Validate and sanitize all external input; test authz boundaries, error paths, and abuse cases; load/perf-check the hot paths.

## Scale

Design for growth — pagination, indexing, caching, background jobs, observability, and alerting.

## Plan For

Trust and safety. Assume adversarial users.

---

This profile is generated from the "Who will use this app?" intake answer (`audience_tier`). It is planning guidance for the Architect — it does not add code or runtime behavior to your project.
