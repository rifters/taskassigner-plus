# Real-World Test Readiness Review

**Reviewed:** 2026-09-02
**Scope:** Determine what remains before a controlled restaurant pilot; no production source changes made by this review.

## Current position

TaskAssigner+ is feature-complete for the core controlled-pilot workflow:

- manager setup of people, job codes, task templates, exclusions, and numbered master lists;
- weekly draft generation, fairness review, constrained edits, posting, and browser printing;
- crew PIN login, grouped task viewing, completion, and write-once notes;
- manager completion/on-behalf actions and review;
- owner reporting and optional weekly email scheduling;
- audit events, CSRF-protected browser forms, rate-limit/lockout logic, and SQLite backup/scheduler utilities.

Verification currently recorded:

- full suite: `68 passed`;
- Sprint 007 focused tests: `16 passed`;
- compile and `git diff --check`: passed;
- demo reset: `DEMO_RESET_OK`;
- HTTP smoke checks: `/health`, `/auth/login-crew`, and combined CSV export returned `200`.

This is **not yet ready for unrestricted production use**. It is close to a controlled pilot after the blockers below are addressed and the complete workflow is manually exercised with realistic data.

## Findings ordered by risk

### P0 — Fix before exposing the app to any real user

1. **Credential-management authorization flaw.**
   - `POST /auth/reset-pin` and `POST /auth/reset-password/request` authenticate the manager by a caller-supplied `actor_name` in JSON.
   - They are not protected by `@role_required("manager")`.
   - A caller who knows a manager's name can attempt manager-only credential actions without an authenticated manager session.
   - Required fix: use the authenticated session (`current_user`), add manager authorization, remove caller-supplied actor identity, add negative tests for unauthenticated and non-manager callers, and audit the action.

2. **Production configuration is unsafe by default.**
   - `SECRET_KEY` falls back to `dev-change-me`.
   - `src/run.py` starts Flask with `debug=True`.
   - Development defaults enable `DEMO_MODE`; a pilot must explicitly run with production settings and demo reset disabled.
   - Required fix/configuration: fail fast when production has no strong secret, run behind a production WSGI server or equivalent service, set an explicit database path, and verify secure session/cookie settings for the HTTPS tunnel.

### P1 — Required before the pilot, even if access stays private

3. **Backup and recovery are not operationally proven.**
   - The backup utility copies the SQLite file to one fixed filename and has no retention, rotation, failure alert, or restore procedure.
   - A direct file copy while the app is writing is not a sufficient recovery policy.
   - Required: choose the backup destination, retention, schedule, and restore owner; perform a real restore into a separate database; verify records and login; document the result.

4. **Deployment/runbook is incomplete.**
   - There is no locked dependency manifest, service definition, deployment configuration, or documented startup/shutdown procedure.
   - Cloudflare Tunnel/Tailscale are described architecturally but are not verified against this running app.
   - Required: document the actual host, Python environment, database location, process supervision, tunnel route, access policy, and rollback procedure.

5. **The end-to-end browser workflow has only route-level automated coverage.**
   - The suite proves backend behavior and rendered-page responses, but not a full phone/desktop journey through the real deployed URL.
   - Required manual pass: manager login → setup/import → exclusions → generate → review/edit → post → print; crew login on phone-sized viewport → view → complete → note; manager review/confirmation; owner report/email test.

6. **Realistic production data has not been loaded and reconciled.**
   - Demo data is only a smoke fixture: 6 people, 4 job codes, 8 task templates, 1 exclusion.
   - Required: prepare the actual first roster, job-code memberships, task master lists, exclusions, and credentials/PIN distribution; import into a non-demo database; reconcile counts and sample records before posting a live week.

7. **Owner email scheduling needs a real dry-run and delivery test.**
   - The code and tests exist, but SMTP, recipient, UTC schedule, Windows Task Scheduler execution, and failure alerting are environment-specific.
   - Required: configure without putting secrets in the repository, run dry-run, send a test message, verify the received content, then test the scheduled runner and its non-zero failure behavior.

### P2 — Recommended before or during the controlled pilot

8. **Add pilot observability.** Verify `/health` externally, retain application logs safely, and define who receives an outage or scheduler failure alert.

9. **Harden data lifecycle behavior.** Confirm the pilot procedure for deactivating people/tasks, deleting records, preserving audit history, and recovering from an accidental import or post.

10. **Clean technical debt and documentation drift.** Replace remaining `Query.get()` calls with `db.session.get()`, add a dependency lock/requirements file, and refresh the top-level sprint metadata in `planning/ARCHITECT_BRIEFING.md` (it still begins with Sprint 002 even though later closeouts are appended).

11. **Confirm the pilot's operating boundary.** The pilot must explicitly exclude schedule/availability imports, capacity limits, weighting, multi-location support, native mobile, notifications, and automatic source-omission deactivation.

## Initial execution sequence

### Gate 1 — Security and production-mode correction

- Fix and test the credential-management authorization flaw.
- Add production configuration validation and disable debug/demo behavior.
- Verify CSRF and session-cookie behavior through the actual HTTPS access path.
- Re-run the full suite and negative authorization tests.

### Gate 2 — Package the actual operating environment

- Decide the host machine and persistent database path.
- Create a reproducible environment/dependency manifest.
- Run the app under a supervised non-debug process.
- Configure Cloudflare Tunnel for crew access and Tailscale/private access for management.
- Confirm only intended routes are reachable from each access path.

### Gate 3 — Recovery and monitoring

- Configure scheduled backups with retention.
- Perform and record a restore drill.
- Configure health monitoring and an alert destination.
- Configure and test the owner-email scheduler, including a deliberate failure test.

### Gate 4 — Data and acceptance rehearsal

- Build the real import files and a credential/PIN distribution plan.
- Import into a fresh pilot database.
- Reconcile every job code, person, task number, active state, and exclusion.
- Run one complete simulated week with realistic assignments and completion activity.
- Confirm printed output and owner reporting match the manager's review.

### Gate 5 — Controlled pilot

- Start with one location and a limited crew group.
- Keep the existing paper process as fallback for the first cycle.
- Record defects, usability friction, assignment fairness issues, missed completions, and recovery events.
- Do not expand scope or declare production-ready until the pilot exit criteria are reviewed.

## Pilot-ready definition

The app is ready for a controlled real-world test when:

- P0 security issues are fixed and covered by tests;
- production mode is explicitly configured with debug/demo disabled;
- the deployed URL works over the intended access paths;
- backup and restore have passed on the real host;
- monitoring and owner-email behavior have been tested;
- realistic data has been reconciled;
- one full manager-to-crew-to-report workflow has passed manually;
- the paper fallback and pilot owner are identified; and
- open defects are documented with explicit accept/defer decisions.

The app should not be called production-ready merely because the automated suite is green.
