============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "009-controlled-pilot-readiness",
  "updated": "2026-09-02T00:00:00-04:00"
}

============================================================
FILE: planning/sprints/009-controlled-pilot-readiness/requirements.md
============================================================
# Sprint 009 Requirements — Controlled Pilot Readiness

## Sprint Goal

Prepare TaskAssigner+ for a controlled real-world restaurant pilot by closing the known credential-authorization flaw, validating operational recovery and monitoring, and rehearsing the complete manager-to-crew-to-report workflow with realistic pilot data. This sprint is hardening and validation, not feature expansion.

## In Scope

1. Require an authenticated, authorized manager or owner session for every privileged credential-management action, including password-reset request and PIN-reset routes. Ignore caller-supplied identity as an authorization grant.
2. Add regression coverage for unauthenticated, unauthorized, forged-actor, CSRF, and successful authorized credential-management paths without exposing credentials or reset tokens.
3. Define and verify explicit pilot/production configuration: demo mode disabled, safe cookie/session settings, supervised host/access path, SMTP configuration guards, and scheduler invocation.
4. Define backup destination, schedule, retention, ownership, failure handling, and restore procedure for the SQLite database.
5. Perform a real restore drill into a separate database and verify schema, users, assignments, completions, audit history, and authorized login without logging or displaying secrets.
6. Verify health monitoring, application error visibility, scheduler failure visibility, and manager/owner alert destinations using safe test signals.
7. Prepare realistic pilot data in a fresh non-demo database: roster, roles, job-code memberships, task master lists, exclusions, and approved credential/PIN distribution procedure. Do not store credentials in planning artifacts or logs.
8. Execute and record a manual end-to-end rehearsal covering Thursday–Wednesday generation, review, posting, crew completion, manager on-behalf completion, prior-week finalization, statistics, and weekly email reporting.
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

## Safety and Data Rules

- Never place passwords, PINs, hashes, tokens, API keys, SMTP secrets, or connection strings in source, tests, planning files, pages, or logs.
- Use redacted fixtures and environment/configuration placeholders for operational tests.
- Do not commit, push, or alter unrelated user files.

============================================================
FILE: planning/sprints/009-controlled-pilot-readiness/blueprint.md
============================================================
# Sprint 009 Blueprint — Controlled Pilot Readiness

## 1. Authorization Hardening

Inspect `src/taskassigner/routes/auth.py`, `src/taskassigner/security.py`, existing role guards, CSRF helpers, audit helpers, and auth tests before editing. For password-reset requests and PIN-reset actions, establish authorization from the authenticated session and server-side target lookup. A form/API `actor_name` may be retained only as display or compatibility input; it must never grant manager authority. Preserve rate limits, lockouts, CSRF, safe response behavior, and audit attribution. Never return reset tokens or credentials in test output.

Test the matrix: anonymous denied, crew/shift lead denied where applicable, manager/owner allowed only for permitted targets, forged actor rejected, invalid target handled safely, CSRF rejected, and successful authorized action audited.

## 2. Pilot Configuration and Operations

Inspect existing config, startup entrypoint, owner scheduler route/script, SMTP guards, health route, and `docs/OPERATIONS.md`. Add only the minimum configuration checks/documentation needed to make pilot mode explicit and fail closed where unsafe. Demo reset/seed must remain development-only. Document the supervised process, Cloudflare/Tailscale access boundary as applicable, scheduler command/trigger, log location and redaction expectations, and operator ownership. Do not add deployment infrastructure.

## 3. Backup and Restore Drill

Use the existing SQLite backup utility. Document destination, naming/retention, schedule, permissions, failure handling, and restore owner. Run the backup against a disposable or pilot fixture, restore to a separate database, initialize/upgrade schema, and verify representative records and authorized login. Capture only safe evidence: paths may be generalized and secrets must be redacted. Add or extend tests for retention/restore behavior only where the existing utility has a testable gap.

## 4. Monitoring and Email Verification

Verify `/health` through the intended access path, application error visibility, scheduler failure visibility, and alert destination. Exercise email rendering and recipient resolution using a captured test transport or equivalent; do not send unsolicited real mail. Confirm a failed scheduled run is visible to the operator. Keep the existing recipient rule: active managers and owners with valid deduplicated addresses; no crew or shift leads.

## 5. Realistic Rehearsal and Runbook

Create a non-secret pilot data checklist and use a fresh non-demo database or disposable pilot fixture. Reconcile counts for people, roles, job codes, task templates, numbers, exclusions, and expected weekly assignments. Manually execute one complete Thursday–Wednesday cycle, including a crew self-completion, a manager on-behalf completion with reason, an unfinished assignment finalized as `not_completed`, statistics, and the summary email plus CSV attachment. Record pass/fail evidence in the runbook and define paper fallback, rollback, pilot owner, and exit criteria.

## Validation

Run focused auth/CSRF/backup/email tests, the full suite, compilation, `git diff --check`, database initialization, backup/restore drill, demo reset safety check, and local HTTP/browser smoke for manager and crew workflows. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, `docs/API.md`, and `docs/OPERATIONS.md` only with verified results.

============================================================
FILE: planning/sprints/009-controlled-pilot-readiness/acceptance.md
============================================================
# Sprint 009 Acceptance — Controlled Pilot Readiness

- [ ] Anonymous requests cannot perform privileged credential-management actions.
- [ ] Crew and unauthorized roles cannot perform manager/owner credential actions.
- [ ] Caller-supplied `actor_name` cannot grant or spoof authorization.
- [ ] Authorized manager/owner flows succeed only for permitted targets and create safe audit events.
- [ ] CSRF, rate-limit, lockout, invalid-target, and failure paths remain enforced and tested.
- [ ] No passwords, PINs, hashes, reset tokens, secrets, or connection strings appear in pages, logs, tests, or planning artifacts.
- [ ] Pilot configuration explicitly disables demo mode and documents supervised access and scheduler operation.
- [ ] Backup destination, schedule, retention, permissions, failure handling, and owner are documented.
- [ ] A restore drill succeeds into a separate database.
- [ ] Restored schema, users, assignments, completions, audit history, and authorized login are verified.
- [ ] Health monitoring and application/scheduler failure visibility are verified with a defined alert destination.
- [ ] Weekly email rendering, recipient resolution, and CSV attachment are verified using a safe captured test path.
- [ ] Fresh realistic pilot data is reconciled without storing credentials in project artifacts.
- [ ] A full Thursday–Wednesday manager-to-crew-to-report rehearsal passes.
- [ ] The rehearsal verifies crew self-completion, manager on-behalf completion, prior-week `not_completed` finalization, statistics, and email reporting.
- [ ] Pilot runbook includes owner, access procedure, paper fallback, rollback/recovery, incident steps, and go/no-go checklist.
- [ ] Existing assignment, completion, reporting, API, and audit behavior remains green.
- [ ] Schedule import, weighting/capacity, multi-location, native mobile, custom PDF, and unrelated feature work remain deferred.
- [ ] Full tests, compilation, whitespace checks, database initialization, and local smoke validation pass.

## Pilot Decision

The sprint is complete only when the checklist has an explicit **GO**, **NO-GO**, or **GO WITH CONDITIONS** decision. Passing automated tests alone is not a pilot approval.

============================================================
FILE: planning/sprints/009-controlled-pilot-readiness/handoff-prompt.md
============================================================
# Builder Handoff — Sprint 009 Controlled Pilot Readiness

Implement only from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current auth routes/security helpers, CSRF and audit patterns, config/startup, scheduler/email paths, backup utility, operations docs, and relevant tests.

Before editing any source or test file, stop at the Builder code gate and provide a concrete file-by-file implementation plan, scope guards, and acceptance mapping. Wait for explicit approval of that implementation plan.

First close the P0 credential-management authorization flaw. Authorization must come from the authenticated session and server-side role/target checks; a submitted actor name must never grant authority. Preserve CSRF, rate limiting, lockouts, safe errors, auditability, and secret-safe output. Add focused abuse/regression coverage.

Then perform only the minimum pilot hardening and verification described in the sprint files: explicit production/demo configuration checks, supervised access and scheduler documentation, backup/restore drill, monitoring and failure visibility, safe email verification, realistic non-secret pilot-data rehearsal, and the pilot runbook/go/no-go checklist. Do not add schedule importing, weighting, capacity, multi-location, native mobile, custom PDF, deployment automation, or unrelated refactors.

Do not send unsolicited email, expose credentials, commit, push, or modify unrelated files. Run focused tests, full tests, compileall, `git diff --check`, schema initialization, backup/restore verification, demo safety checks, and real local HTTP/browser smoke checks. Update planning and operations documentation only after evidence exists.
