# Sprint 009 Requirements — Controlled Pilot Readiness

## Sprint Goal

Prepare TaskAssigner+ for a controlled real-world restaurant pilot by closing the known credential-authorization flaw, validating all locally testable recovery and monitoring behavior, and rehearsing the complete manager-to-crew-to-report workflow with realistic pilot data. Host installation, hosting, external monitoring, and production SMTP remain explicitly deferred until the host PC is available.

## In Scope

1. Require an authenticated, authorized manager or owner session for every privileged credential-management action, including password-reset request and PIN-reset routes. Ignore caller-supplied identity as an authorization grant.
2. Add regression coverage for unauthenticated, unauthorized, forged-actor, CSRF, and successful authorized credential-management paths without exposing credentials or reset tokens.
3. Define and locally verify explicit pilot/production configuration: demo mode disabled, safe cookie/session settings, SMTP configuration guards, and scheduler invocation. Document the host-dependent steps for later execution.
4. Define backup destination, schedule, retention, ownership, failure handling, and restore procedure for the SQLite database; verify the backup/restore mechanics locally.
5. Perform a real restore drill into a separate database and verify schema, users, assignments, completions, audit history, and authorized login without logging or displaying secrets.
6. Verify locally testable health, application error, and scheduler failure behavior. Document external monitoring and alert setup for the host-PC phase.
7. Prepare realistic pilot data in a fresh non-demo database: roster, roles, job-code memberships, task master lists, exclusions, and approved credential/PIN distribution procedure. Do not store credentials in planning artifacts or logs.
8. Execute and record a local manual end-to-end rehearsal covering Thursday–Wednesday generation, review, posting, crew completion, manager on-behalf completion, prior-week finalization, statistics, and weekly email rendering.
9. Produce a concise pilot runbook, rollback/paper fallback procedure, and go/no-go checklist.
10. Preserve existing JSON/API contracts, assignment eligibility, completion semantics, reporting behavior, auditability, and scope exclusions.

## Out of Scope

- Schedule or availability importing
- Task weighting, capacity limits, or new fairness algorithms
- Multi-location support or tenantization
- Native mobile app, frontend framework, or build pipeline
- Custom PDF generation
- New dashboards or analytics beyond pilot verification
- SMTP provider migration or credential-management redesign beyond the authorization flaw
- Automatic production deployment or public launch
- Host-PC installation, hosting, Cloudflare/Tailscale configuration, external uptime monitoring, production SMTP delivery, and real scheduler registration until the host PC is available

## Safety and Data Rules

- Never place passwords, PINs, hashes, tokens, API keys, SMTP secrets, or connection strings in source, tests, planning files, pages, or logs.
- Use redacted fixtures and environment/configuration placeholders for operational tests.
- Do not commit, push, or alter unrelated user files.
